/**
 * Isengard Verb Processor Implementation
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#include "Isengard_VerbProcessor.h"
#include "Isengard_DSP.h"
#include "Isengard_FDN.h"

namespace Isengard
{
    // ============================================================================
    // VerbModeBase Implementation
    // ============================================================================
    
    VerbModeBase::VerbModeBase(double sampleRate)
        : sampleRate(sampleRate)
    {
    }
    
    VerbModeBase::~VerbModeBase()
    {
    }
    
    void VerbModeBase::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
    }
    
    void VerbModeBase::setParameter(const juce::String& paramName, float value)
    {
        // Base implementation does nothing
    }
    
    void VerbModeBase::reset()
    {
    }
    
    // ============================================================================
    // ColorSystem Implementation
    // ============================================================================
    
    ColorSystem::ColorSystem(double sampleRate, ColorType color)
        : sampleRate(sampleRate),
          color(color),
          dampingFilter(nullptr),
          toneFilter(nullptr),
          dampingAmount(0.5f),
          toneAmount(0.5f)
    {
        dampingFilter = new OnePoleFilter(5000.0, sampleRate, OnePoleFilter::LOWPASS);
        toneFilter = new BiquadFilter(1000.0, 0.707f, 0.0f, sampleRate, BiquadFilter::LOWSHELF);
    }
    
    ColorSystem::~ColorSystem()
    {
        delete dampingFilter;
        delete toneFilter;
    }
    
    void ColorSystem::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        if (dampingFilter) dampingFilter->setSampleRate(sampleRate);
        if (toneFilter) toneFilter->setSampleRate(sampleRate);
    }
    
    void ColorSystem::setColor(ColorType color)
    {
        this->color = color;
        
        // Configure filters based on color
        switch (color)
        {
            case COLOR_1970S:
                // Warmer, darker
                dampingAmount = 0.7f;
                toneAmount = -6.0f; // Cut highs
                if (dampingFilter) dampingFilter->setCutoff(3000.0);
                break;
            case COLOR_1980S:
                // Clean, balanced
                dampingAmount = 0.5f;
                toneAmount = 0.0f;
                if (dampingFilter) dampingFilter->setCutoff(5000.0);
                break;
            case COLOR_NOW:
                // Transparent, bright
                dampingAmount = 0.3f;
                toneAmount = 6.0f; // Boost highs
                if (dampingFilter) dampingFilter->setCutoff(8000.0);
                break;
        }
    }
    
    float ColorSystem::process(float input)
    {
        float out = dampingFilter->process(input);
        out = toneFilter->process(out);
        return out;
    }
    
    void ColorSystem::processBlock(const float* input, float* output, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            output[i] = process(input[i]);
        }
    }
    
    void ColorSystem::reset()
    {
        if (dampingFilter) dampingFilter->reset();
        if (toneFilter) toneFilter->reset();
    }
    
    // ============================================================================
    // VerbProcessor Implementation
    // ============================================================================
    
    VerbProcessor::VerbProcessor(double sampleRate)
        : sampleRate(sampleRate),
          currentMode(MODE_1978),
          currentColor(COLOR_1980S),
          modeProcessor(nullptr),
          colorSystem(nullptr),
          earlyReflections(nullptr),
          modulationMatrix(nullptr),
          fdnReverb(nullptr),
          inputHighpass(nullptr),
          inputLowpass(nullptr),
          outputHighpass(nullptr),
          outputLowpass(nullptr),
          highCutFilter(nullptr),
          lowCutFilter(nullptr)
    {
        // Create filters
        inputHighpass = new OnePoleFilter(20.0, sampleRate, OnePoleFilter::HIGHPASS);
        inputLowpass = new OnePoleFilter(20000.0, sampleRate, OnePoleFilter::LOWPASS);
        outputHighpass = new OnePoleFilter(20.0, sampleRate, OnePoleFilter::HIGHPASS);
        outputLowpass = new OnePoleFilter(20000.0, sampleRate, OnePoleFilter::LOWPASS);
        highCutFilter = new BiquadFilter(10000.0, 0.707f, 0.0f, sampleRate, BiquadFilter::LOWPASS);
        lowCutFilter = new BiquadFilter(200.0, 0.707f, 0.0f, sampleRate, BiquadFilter::HIGHPASS);
        
        // Create FDN reverb
        fdnReverb = new FDNReverb(sampleRate);
        
        // Create mode processor
        modeProcessor = createModeProcessor(currentMode);
        
        // Create color system
        colorSystem = new ColorSystem(sampleRate, static_cast<ColorSystem::ColorType>(currentColor));
        
        // Initialize parameters
        initializeDefaultParameters();
        
        // Configure FDN with mode settings
        if (modeProcessor && fdnReverb)
            modeProcessor->configureFDN(fdnReverb);
    }
    
    VerbProcessor::~VerbProcessor()
    {
        delete modeProcessor;
        delete colorSystem;
        delete earlyReflections;
        delete modulationMatrix;
        delete fdnReverb;
        
        delete inputHighpass;
        delete inputLowpass;
        delete outputHighpass;
        delete outputLowpass;
        delete highCutFilter;
        delete lowCutFilter;
    }
    
    void VerbProcessor::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        
        if (inputHighpass) inputHighpass->setSampleRate(sampleRate);
        if (inputLowpass) inputLowpass->setSampleRate(sampleRate);
        if (outputHighpass) outputHighpass->setSampleRate(sampleRate);
        if (outputLowpass) outputLowpass->setSampleRate(sampleRate);
        if (highCutFilter) highCutFilter->setSampleRate(sampleRate);
        if (lowCutFilter) lowCutFilter->setSampleRate(sampleRate);
        
        if (fdnReverb) fdnReverb->setSampleRate(sampleRate);
        if (modeProcessor) modeProcessor->setSampleRate(sampleRate);
        if (colorSystem) colorSystem->setSampleRate(sampleRate);
    }
    
    void VerbProcessor::setMode(Mode mode)
    {
        if (mode >= 0 && mode < NUM_MODES)
        {
            currentMode = mode;
            delete modeProcessor;
            modeProcessor = createModeProcessor(mode);
            modeProcessor->setSampleRate(sampleRate);
            
            // Reconfigure FDN
            if (modeProcessor && fdnReverb)
                modeProcessor->configureFDN(fdnReverb);
        }
    }
    
    void VerbProcessor::setMode(const juce::String& modeName)
    {
        juce::String lowerName = modeName.toLowerCase();
        
        if (lowerName == "1972" || lowerName.contains("1972")) setMode(MODE_1972);
        else if (lowerName == "1974" || lowerName.contains("1974")) setMode(MODE_1974);
        else if (lowerName == "1975" || lowerName.contains("1975")) setMode(MODE_1975);
        else if (lowerName == "1976" || lowerName.contains("1976")) setMode(MODE_1976);
        else if (lowerName == "1977" || lowerName.contains("1977")) setMode(MODE_1977);
        else if (lowerName == "1978" || lowerName.contains("1978")) setMode(MODE_1978);
        else if (lowerName == "1979" || lowerName.contains("1979")) setMode(MODE_1979);
        else if (lowerName == "1980" || lowerName.contains("1980")) setMode(MODE_1980);
        else if (lowerName == "1981" || lowerName.contains("1981")) setMode(MODE_1981);
        else if (lowerName == "1982" || lowerName.contains("1982")) setMode(MODE_1982);
        else if (lowerName == "1983" || lowerName.contains("1983")) setMode(MODE_1983);
        else if (lowerName == "1984" || lowerName.contains("1984")) setMode(MODE_1984);
        else if (lowerName == "1985" || lowerName.contains("1985")) setMode(MODE_1985);
        else if (lowerName == "1986" || lowerName.contains("1986")) setMode(MODE_1986);
        else if (lowerName == "1987" || lowerName.contains("1987")) setMode(MODE_1987);
        else if (lowerName == "1990" || lowerName.contains("1990")) setMode(MODE_1990);
        else if (lowerName == "1991" || lowerName.contains("1991")) setMode(MODE_1991);
        else if (lowerName == "1992" || lowerName.contains("1992")) setMode(MODE_1992);
        else if (lowerName == "1993" || lowerName.contains("1993")) setMode(MODE_1993);
        else if (lowerName == "1994" || lowerName.contains("1994")) setMode(MODE_1994);
        else if (lowerName == "1995" || lowerName.contains("1995")) setMode(MODE_1995);
        else if (lowerName == "now1" || lowerName.contains("now1")) setMode(MODE_NOW1);
        else if (lowerName == "now2" || lowerName.contains("now2")) setMode(MODE_NOW2);
    }
    
    void VerbProcessor::setColor(Color color)
    {
        if (color >= 0 && color < NUM_COLORS)
        {
            currentColor = color;
            if (colorSystem)
                colorSystem->setColor(static_cast<ColorSystem::ColorType>(color));
        }
    }
    
    void VerbProcessor::setColor(const juce::String& colorName)
    {
        juce::String lowerName = colorName.toLowerCase();
        
        if (lowerName == "1970s" || lowerName.contains("1970")) setColor(COLOR_1970S);
        else if (lowerName == "1980s" || lowerName.contains("1980")) setColor(COLOR_1980S);
        else if (lowerName == "now") setColor(COLOR_NOW);
    }
    
    void VerbProcessor::setParameters(const std::map<juce::String, float>& params)
    {
        for (const auto& pair : params)
        {
            setParameter(pair.first, pair.second);
        }
    }
    
    void VerbProcessor::setParameter(const juce::String& paramName, float value)
    {
        params[paramName] = value;
        
        if (modeProcessor)
            modeProcessor->setParameter(paramName, value);
        if (fdnReverb)
        {
            if (paramName == "decay") fdnReverb->setDecay(value);
            else if (paramName == "size") fdnReverb->setSize(value);
            else if (paramName == "diffusion") fdnReverb->setDiffusion(value);
            else if (paramName == "damping") fdnReverb->setDamping(value);
        }
        if (colorSystem)
        {
            if (paramName == "color") setColor(static_cast<int>(value));
        }
    }
    
    float VerbProcessor::processSample(float input)
    {
        // Process through input filters
        float filtered = inputHighpass->process(input);
        filtered = inputLowpass->process(filtered);
        
        // Process through FDN reverb
        float reverbOut = fdnReverb->process(filtered);
        
        // Apply color
        float colored = colorSystem->process(reverbOut);
        
        // Process through output filters
        float output = outputHighpass->process(colored);
        output = outputLowpass->process(output);
        
        // Apply high/low cut
        output = highCutFilter->process(output);
        output = lowCutFilter->process(output);
        
        // Apply mix (simplified)
        float mix = params.count("mix") ? params["mix"] : 0.5f;
        output = input * (1.0f - mix) + output * mix;
        
        return denormalPrevent(output);
    }
    
    std::pair<float, float> VerbProcessor::processSample(float leftInput, float rightInput)
    {
        float outL = processSample(leftInput);
        float outR = processSample(rightInput);
        return {outL, outR};
    }
    
    void VerbProcessor::processBlock(const float* inputL, const float* inputR, float* outputL, float* outputR, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            auto [outL, outR] = processSample(inputL[i], inputR[i]);
            outputL[i] = outL;
            outputR[i] = outR;
        }
    }
    
    void VerbProcessor::reset()
    {
        if (inputHighpass) inputHighpass->reset();
        if (inputLowpass) inputLowpass->reset();
        if (outputHighpass) outputHighpass->reset();
        if (outputLowpass) outputLowpass->reset();
        if (highCutFilter) highCutFilter->reset();
        if (lowCutFilter) lowCutFilter->reset();
        if (fdnReverb) fdnReverb->reset();
        if (modeProcessor) modeProcessor->reset();
        if (colorSystem) colorSystem->reset();
    }
    
    VerbModeBase* VerbProcessor::createModeProcessor(Mode mode)
    {
        // For now, create a basic mode processor
        // In a full implementation, each mode would have its own class
        return new VerbModeBase(sampleRate);
    }
    
    void VerbProcessor::initializeDefaultParameters()
    {
        params["mode"] = static_cast<float>(MODE_1978);
        params["color"] = static_cast<float>(COLOR_1980S);
        params["mix"] = 0.5f;
        params["decay"] = 0.5f;
        params["size"] = 0.5f;
        params["pre_delay"] = 50.0f;
        params["attack"] = 0.0f;
        params["bass_mult"] = 1.0f;
        params["bass_xover"] = 200.0f;
        params["high_cut"] = 10000.0f;
        params["damping"] = 0.5f;
        params["damping_freq"] = 10000.0f;
        params["diffusion"] = 0.5f;
        params["mod_rate"] = 0.5f;
        params["mod_depth"] = 0.1f;
        params["width"] = 0.5f;
        params["early_level"] = 0.5f;
    }
}
