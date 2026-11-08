/**
 * Isengard Delay Processor Implementation
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#include "Isengard_DelayProcessor.h"
#include "Isengard_DSP.h"
#include "Isengard_DelayModes.h"
#include "Isengard_DelayStyles.h"

namespace Isengard
{
    // ============================================================================
    // SmoothedParameter Implementation
    // ============================================================================
    
    SmoothedParameter::SmoothedParameter(float initialValue, float minValue, float maxValue,
                                         float smoothTimeMs, double sampleRate)
        : currentValue(initialValue),
          targetValue(initialValue),
          minValue(minValue),
          maxValue(maxValue),
          smoothTimeMs(smoothTimeMs),
          sampleRate(sampleRate)
    {
        updateCoefficient();
    }
    
    SmoothedParameter::~SmoothedParameter()
    {
    }
    
    void SmoothedParameter::setValue(float value)
    {
        targetValue = clamp(value, minValue, maxValue);
    }
    
    float SmoothedParameter::getValue() const
    {
        return currentValue;
    }
    
    float SmoothedParameter::process()
    {
        // Exponential smoothing: current = current + coefficient * (target - current)
        currentValue += coefficient * (targetValue - currentValue);
        return currentValue;
    }
    
    void SmoothedParameter::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        updateCoefficient();
    }
    
    void SmoothedParameter::setSmoothTime(float smoothTimeMs)
    {
        this->smoothTimeMs = smoothTimeMs;
        updateCoefficient();
    }
    
    void SmoothedParameter::reset()
    {
        currentValue = targetValue;
    }
    
    void SmoothedParameter::updateCoefficient()
    {
        if (sampleRate > 0 && smoothTimeMs > 0)
        {
            // coefficient = 1 - exp(-1 / (smoothTimeMs * sampleRate / 1000))
            float samplesPerMs = sampleRate / 1000.0f;
            coefficient = 1.0f - std::exp(-1.0f / (smoothTimeMs * samplesPerMs));
        }
        else
        {
            coefficient = 1.0f; // Instant
        }
    }
    
    // ============================================================================
    // DelayProcessor Implementation
    // ============================================================================
    
    DelayProcessor::DelayProcessor(double sampleRate)
        : sampleRate(sampleRate),
          currentMode(MODE_TAPE),
          currentStyle(STYLE_SINGLE),
          modeProcessor(nullptr),
          styleProcessor(nullptr),
          inputHighpass(nullptr),
          inputLowpass(nullptr),
          outputHighpass(nullptr),
          outputLowpass(nullptr),
          eqHigh(nullptr),
          eqLow(nullptr)
    {
        // Create filters
        inputHighpass = new OnePoleFilter(20.0, sampleRate, OnePoleFilter::HIGHPASS);
        inputLowpass = new OnePoleFilter(20000.0, sampleRate, OnePoleFilter::LOWPASS);
        outputHighpass = new OnePoleFilter(20.0, sampleRate, OnePoleFilter::HIGHPASS);
        outputLowpass = new OnePoleFilter(20000.0, sampleRate, OnePoleFilter::LOWPASS);
        eqHigh = new OnePoleFilter(10000.0, sampleRate, OnePoleFilter::LOWPASS);
        eqLow = new OnePoleFilter(200.0, sampleRate, OnePoleFilter::HIGHPASS);
        
        // Create mode and style processors
        modeProcessor = createModeProcessor(currentMode);
        styleProcessor = createStyleProcessor(currentStyle);
        
        // Initialize parameters and smoothers
        initializeDefaultParameters();
        initializeSmoothers();
    }
    
    DelayProcessor::~DelayProcessor()
    {
        delete modeProcessor;
        delete styleProcessor;
        
        delete inputHighpass;
        delete inputLowpass;
        delete outputHighpass;
        delete outputLowpass;
        delete eqHigh;
        delete eqLow;
        
        // Delete smoothers
        for (auto& pair : smoothers)
        {
            delete pair.second;
        }
        smoothers.clear();
    }
    
    void DelayProcessor::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        
        inputHighpass->setSampleRate(sampleRate);
        inputLowpass->setSampleRate(sampleRate);
        outputHighpass->setSampleRate(sampleRate);
        outputLowpass->setSampleRate(sampleRate);
        eqHigh->setSampleRate(sampleRate);
        eqLow->setSampleRate(sampleRate);
        
        if (modeProcessor)
            modeProcessor->setSampleRate(sampleRate);
        if (styleProcessor)
            styleProcessor->setSampleRate(sampleRate);
        
        for (auto& pair : smoothers)
        {
            pair.second->setSampleRate(sampleRate);
        }
    }
    
    void DelayProcessor::setMode(Mode mode)
    {
        if (mode >= 0 && mode < NUM_MODES)
        {
            currentMode = mode;
            delete modeProcessor;
            modeProcessor = createModeProcessor(mode);
            modeProcessor->setSampleRate(sampleRate);
        }
    }
    
    void DelayProcessor::setMode(const juce::String& modeName)
    {
        juce::String lowerName = modeName.toLowerCase();
        
        if (lowerName == "tape") setMode(MODE_TAPE);
        else if (lowerName == "hifi") setMode(MODE_HIFI);
        else if (lowerName == "bbd") setMode(MODE_BBD);
        else if (lowerName == "digital") setMode(MODE_DIGITAL);
        else if (lowerName == "ghost") setMode(MODE_GHOST);
        else if (lowerName == "pitch") setMode(MODE_PITCH);
        else if (lowerName == "revpitch") setMode(MODE_REVPITCH);
    }
    
    void DelayProcessor::setStyle(Style style)
    {
        if (style >= 0 && style < NUM_STYLES)
        {
            currentStyle = style;
            delete styleProcessor;
            styleProcessor = createStyleProcessor(style);
            styleProcessor->setSampleRate(sampleRate);
        }
    }
    
    void DelayProcessor::setStyle(const juce::String& styleName)
    {
        juce::String lowerName = styleName.toLowerCase();
        
        if (lowerName == "single") setStyle(STYLE_SINGLE);
        else if (lowerName == "dual") setStyle(STYLE_DUAL);
        else if (lowerName == "ratio") setStyle(STYLE_RATIO);
        else if (lowerName == "pingpong" || lowerName == "ping_pong") setStyle(STYLE_PINGPONG);
        else if (lowerName == "quad") setStyle(STYLE_QUAD);
    }
    
    void DelayProcessor::setParameters(const std::map<juce::String, float>& params)
    {
        for (const auto& pair : params)
        {
            setParameter(pair.first, pair.second);
        }
    }
    
    void DelayProcessor::setParameter(const juce::String& paramName, float value)
    {
        params[paramName] = value;
        
        auto it = smoothers.find(paramName);
        if (it != smoothers.end())
        {
            it->second->setValue(value);
        }
        
        // Also update mode/style processors if they have this parameter
        if (modeProcessor)
            modeProcessor->setParameter(paramName, value);
        if (styleProcessor)
            styleProcessor->setParameter(paramName, value);
    }
    
    float DelayProcessor::processSample(float input)
    {
        // Process through input filters
        float filtered = inputHighpass->process(input);
        filtered = inputLowpass->process(filtered);
        
        // Process through mode
        float modeOut = modeProcessor->process(filtered);
        
        // Process through style
        float styleOut = styleProcessor->process(modeOut);
        
        // Process through EQ
        float eqOut = eqHigh->process(styleOut);
        eqOut = eqLow->process(eqOut);
        
        // Process through output filters
        float output = outputHighpass->process(eqOut);
        output = outputLowpass->process(output);
        
        // Apply mix (simplified - no smoothing for now)
        float mix = params.count("mix") ? params["mix"] : 0.5f;
        output = input * (1.0f - mix) + output * mix;
        
        return denormalPrevent(output);
    }
    
    std::pair<float, float> DelayProcessor::processSample(float leftInput, float rightInput)
    {
        float outL = processSample(leftInput);
        float outR = processSample(rightInput);
        return {outL, outR};
    }
    
    void DelayProcessor::processBlock(const float* inputL, const float* inputR, float* outputL, float* outputR, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            auto [outL, outR] = processSample(inputL[i], inputR[i]);
            outputL[i] = outL;
            outputR[i] = outR;
        }
    }
    
    void DelayProcessor::reset()
    {
        inputHighpass->reset();
        inputLowpass->reset();
        outputHighpass->reset();
        outputLowpass->reset();
        eqHigh->reset();
        eqLow->reset();
        
        if (modeProcessor)
            modeProcessor->reset();
        if (styleProcessor)
            styleProcessor->reset();
        
        for (auto& pair : smoothers)
        {
            pair.second->reset();
        }
    }
    
    DelayModeBase* DelayProcessor::createModeProcessor(Mode mode)
    {
        switch (mode)
        {
            case MODE_TAPE:     return new TapeMode(sampleRate);
            case MODE_HIFI:     return new HiFiMode(sampleRate);
            case MODE_BBD:      return new BBDMode(sampleRate);
            case MODE_DIGITAL:  return new DigitalMode(sampleRate);
            case MODE_GHOST:    return new GhostMode(sampleRate);
            case MODE_PITCH:    return new PitchMode(sampleRate);
            case MODE_REVPITCH: return new RevPitchMode(sampleRate);
            default:            return new TapeMode(sampleRate);
        }
    }
    
    DelayStyleBase* DelayProcessor::createStyleProcessor(Style style)
    {
        switch (style)
        {
            case STYLE_SINGLE:   return new SingleStyle(sampleRate);
            case STYLE_DUAL:     return new DualStyle(sampleRate);
            case STYLE_RATIO:    return new RatioStyle(sampleRate);
            case STYLE_PINGPONG: return new PingPongStyle(sampleRate);
            case STYLE_QUAD:     return new QuadStyle(sampleRate);
            default:             return new SingleStyle(sampleRate);
        }
    }
    
    SmoothedParameter* DelayProcessor::createSmoothedParameter(
        const juce::String& name, 
        float defaultValue, 
        float minValue, 
        float maxValue,
        float smoothTimeMs)
    {
        auto* smoother = new SmoothedParameter(defaultValue, minValue, maxValue, smoothTimeMs, sampleRate);
        params[name] = defaultValue;
        return smoother;
    }
    
    void DelayProcessor::initializeSmoothers()
    {
        // Create smoothers for all parameters
        smoothers["mix"] = createSmoothedParameter("mix", 0.5f, 0.0f, 1.0f);
        smoothers["feedback"] = createSmoothedParameter("feedback", 0.5f, 0.0f, 0.99f);
        smoothers["delay_time_ms"] = createSmoothedParameter("delay_time_ms", 500.0f, 1.0f, 5000.0f);
        smoothers["delay_time_l_ms"] = createSmoothedParameter("delay_time_l_ms", 500.0f, 1.0f, 5000.0f);
        smoothers["delay_time_r_ms"] = createSmoothedParameter("delay_time_r_ms", 500.0f, 1.0f, 5000.0f);
        smoothers["ratio"] = createSmoothedParameter("ratio", 0.5f, 0.0f, 1.0f);
        smoothers["spread"] = createSmoothedParameter("spread", 0.5f, 0.0f, 1.0f);
        smoothers["mod_rate"] = createSmoothedParameter("mod_rate", 0.5f, 0.1f, 10.0f);
        smoothers["mod_depth"] = createSmoothedParameter("mod_depth", 0.1f, 0.0f, 1.0f);
        smoothers["age"] = createSmoothedParameter("age", 0.0f, 0.0f, 1.0f);
        smoothers["drive"] = createSmoothedParameter("drive", 0.0f, 0.0f, 1.0f);
        smoothers["diffusion"] = createSmoothedParameter("diffusion", 0.5f, 0.0f, 1.0f);
        smoothers["diffusion_size"] = createSmoothedParameter("diffusion_size", 0.5f, 0.0f, 1.0f);
        smoothers["eq_high"] = createSmoothedParameter("eq_high", 10000.0f, 100.0f, 20000.0f);
        smoothers["eq_low"] = createSmoothedParameter("eq_low", 200.0f, 20.0f, 1000.0f);
        smoothers["era"] = createSmoothedParameter("era", 0.5f, 0.0f, 1.0f);
        smoothers["ducking"] = createSmoothedParameter("ducking", 0.0f, 0.0f, 1.0f);
        smoothers["pitch_shift"] = createSmoothedParameter("pitch_shift", 0.0f, -12.0f, 12.0f);
        smoothers["pitch_detune"] = createSmoothedParameter("pitch_detune", 0.0f, -12.0f, 12.0f);
        smoothers["frequency_shift"] = createSmoothedParameter("frequency_shift", 0.0f, -1.0f, 1.0f);
    }
    
    void DelayProcessor::initializeDefaultParameters()
    {
        params["mode"] = static_cast<float>(MODE_TAPE);
        params["style"] = static_cast<float>(STYLE_SINGLE);
        params["mix"] = 0.5f;
        params["feedback"] = 0.5f;
        params["delay_time_ms"] = 500.0f;
        params["delay_time_l_ms"] = 500.0f;
        params["delay_time_r_ms"] = 500.0f;
        params["ratio"] = 0.5f;
        params["spread"] = 0.5f;
        params["mod_rate"] = 0.5f;
        params["mod_depth"] = 0.1f;
        params["age"] = 0.0f;
        params["drive"] = 0.0f;
        params["diffusion"] = 0.5f;
        params["diffusion_size"] = 0.5f;
        params["eq_high"] = 10000.0f;
        params["eq_low"] = 200.0f;
        params["era"] = 0.5f;
        params["ducking"] = 0.0f;
        params["pitch_shift"] = 0.0f;
        params["pitch_detune"] = 0.0f;
        params["frequency_shift"] = 0.0f;
    }
}
