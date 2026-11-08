/**
 * Isengard DSP - Shared DSP Components Implementation
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#include "Isengard_DSP.h"

namespace Isengard
{
    // ============================================================================
    // Utility Functions
    // ============================================================================
    
    int msToSamples(double ms, double sampleRate)
    {
        return static_cast<int>(std::round(ms * sampleRate / 1000.0));
    }
    
    double samplesToMs(int samples, double sampleRate)
    {
        return static_cast<double>(samples) * 1000.0 / sampleRate;
    }
    
    float cubicInterpolate(const float* data, float fractionalIndex, int bufferSize)
    {
        // Clamp fractional index
        fractionalIndex = clamp(fractionalIndex, 0.0f, static_cast<float>(bufferSize - 1));
        
        int x0 = static_cast<int>(fractionalIndex) - 1;
        int x1 = static_cast<int>(fractionalIndex);
        int x2 = static_cast<int>(fractionalIndex) + 1;
        int x3 = static_cast<int>(fractionalIndex) + 2;
        
        // Clamp indices
        x0 = juce::jlimit(0, bufferSize - 1, x0);
        x1 = juce::jlimit(0, bufferSize - 1, x1);
        x2 = juce::jlimit(0, bufferSize - 1, x2);
        x3 = juce::jlimit(0, bufferSize - 1, x3);
        
        float a = -0.5f * data[x0] + 1.5f * data[x1] - 1.5f * data[x2] + 0.5f * data[x3];
        float b = data[x0] - 2.5f * data[x1] + 2.0f * data[x2] - 0.5f * data[x3];
        float c = -0.5f * data[x0] + 0.5f * data[x2];
        float d = data[x1];
        
        float fractional = fractionalIndex - static_cast<float>(x1);
        return ((a * fractional + b) * fractional + c) * fractional + d;
    }
    
    float denormalPrevent(float x)
    {
        // Add tiny noise to prevent denormal numbers
        static const float denormalFix = 1e-20f;
        return x + denormalFix;
    }
    
    // ============================================================================
    // DelayLine Implementation
    // ============================================================================
    
    DelayLine::DelayLine(double maxDelaySeconds, double sampleRate)
        : sampleRate(sampleRate),
          maxDelaySeconds(maxDelaySeconds),
          writePos(0),
          delaySeconds(0.0),
          delaySamples(0.0)
    {
        bufferSize = static_cast<int>(std::ceil(maxDelaySeconds * sampleRate));
        // Make buffer size a power of 2 for efficient modulo
        if (bufferSize < 8)
            bufferSize = 8;
        else
        {
            bufferSize = 1;
            while (bufferSize < static_cast<int>(maxDelaySeconds * sampleRate))
                bufferSize *= 2;
        }
        
        buffer.calloc(bufferSize + 4); // +4 for cubic interpolation safety
        std::memset(buffer.getData(), 0, bufferSize * sizeof(float));
        
        for (int i = 0; i < 4; ++i)
        {
            prevReadPos[i] = 0;
            prevSamples[i] = 0.0f;
        }
    }
    
    DelayLine::~DelayLine()
    {
    }
    
    void DelayLine::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        // Recalculate buffer size
        int newBufferSize = static_cast<int>(std::ceil(maxDelaySeconds * sampleRate));
        if (newBufferSize > bufferSize)
        {
            bufferSize = 1;
            while (bufferSize < newBufferSize)
                bufferSize *= 2;
            buffer.calloc(bufferSize + 4);
        }
    }
    
    void DelayLine::setDelayTime(double delaySeconds)
    {
        this->delaySeconds = clamp(delaySeconds, 0.0, maxDelaySeconds);
        this->delaySamples = delaySeconds * sampleRate;
    }
    
    void DelayLine::setDelayMs(double delayMs)
    {
        setDelayTime(delayMs / 1000.0);
    }
    
    float DelayLine::process(float input)
    {
        // Write to buffer
        buffer[writePos] = denormalPrevent(input);
        
        // Calculate read position
        int readPos = calculateReadPosition();
        
        // Read with interpolation
        float output = readWithInterpolation(readPos);
        
        // Update write position
        writePos = (writePos + 1) % bufferSize;
        
        return output;
    }
    
    float DelayLine::read() const
    {
        int readPos = calculateReadPosition();
        return readWithInterpolation(readPos);
    }
    
    void DelayLine::processBlock(const float* input, float* output, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            output[i] = process(input[i]);
        }
    }
    
    void DelayLine::reset()
    {
        std::memset(buffer.getData(), 0, bufferSize * sizeof(float));
        writePos = 0;
        for (int i = 0; i < 4; ++i)
        {
            prevReadPos[i] = 0;
            prevSamples[i] = 0.0f;
        }
    }
    
    int DelayLine::calculateReadPosition() const
    {
        double readPosDouble = static_cast<double>(writePos) - delaySamples;
        // Handle negative read positions (wrap around)
        while (readPosDouble < 0)
            readPosDouble += bufferSize;
        return static_cast<int>(readPosDouble) % bufferSize;
    }
    
    float DelayLine::readWithInterpolation(int readPos) const
    {
        // For now, use linear interpolation for simplicity
        // Can be upgraded to cubic later
        float fractional = static_cast<float>(delaySamples) - std::floor(delaySamples);
        int index0 = readPos;
        int index1 = (readPos + 1) % bufferSize;
        
        return lerp(buffer[index0], buffer[index1], fractional);
    }
    
    // ============================================================================
    // OnePoleFilter Implementation
    // ============================================================================
    
    OnePoleFilter::OnePoleFilter(double cutoffHz, double sampleRate, FilterType type)
        : sampleRate(sampleRate),
          cutoffHz(cutoffHz),
          type(type),
          y1(0.0f)
    {
        updateCoefficients();
    }
    
    OnePoleFilter::~OnePoleFilter()
    {
    }
    
    void OnePoleFilter::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        updateCoefficients();
    }
    
    void OnePoleFilter::setCutoff(double cutoffHz)
    {
        this->cutoffHz = clamp(cutoffHz, 1.0, sampleRate * 0.5);
        updateCoefficients();
    }
    
    void OnePoleFilter::setType(FilterType type)
    {
        this->type = type;
        updateCoefficients();
    }
    
    void OnePoleFilter::updateCoefficients()
    {
        if (sampleRate <= 0) return;
        
        double wc = 2.0 * PI * cutoffHz / sampleRate;
        
        if (type == LOWPASS)
        {
            // Lowpass: y[n] = a * x[n] + (1 - a) * y[n-1]
            // a = 1 - exp(-wc)
            a = static_cast<float>(1.0 - std::exp(-wc));
        }
        else // HIGHPASS
        {
            // Highpass: y[n] = a * (x[n] - x[n-1]) + (1 - a) * y[n-1]
            // a = exp(-wc)
            a = static_cast<float>(std::exp(-wc));
        }
    }
    
    float OnePoleFilter::process(float input)
    {
        if (type == LOWPASS)
        {
            y1 = a * input + (1.0f - a) * y1;
            return y1;
        }
        else // HIGHPASS
        {
            float output = a * (input - prevInput) + (1.0f - a) * y1;
            prevInput = input;
            y1 = output;
            return output;
        }
    }
    
    void OnePoleFilter::processBlock(const float* input, float* output, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            output[i] = process(input[i]);
        }
    }
    
    void OnePoleFilter::reset()
    {
        y1 = 0.0f;
        prevInput = 0.0f;
    }
    
    // ============================================================================
    // BiquadFilter Implementation
    // ============================================================================
    
    BiquadFilter::BiquadFilter(double freq, double Q, double gainDB, double sampleRate, FilterType type)
        : sampleRate(sampleRate),
          freq(freq),
          Q(Q),
          gainDB(gainDB),
          type(type),
          x1(0.0f), x2(0.0f), y1(0.0f), y2(0.0f)
    {
        updateCoefficients();
    }
    
    BiquadFilter::~BiquadFilter()
    {
    }
    
    void BiquadFilter::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        updateCoefficients();
    }
    
    void BiquadFilter::setParameters(double freq, double Q, double gainDB)
    {
        this->freq = freq;
        this->Q = Q;
        this->gainDB = gainDB;
        updateCoefficients();
    }
    
    void BiquadFilter::setType(FilterType type)
    {
        this->type = type;
        updateCoefficients();
    }
    
    void BiquadFilter::updateCoefficients()
    {
        if (sampleRate <= 0) return;
        
        double w0 = 2.0 * PI * freq / sampleRate;
        double cosW0 = std::cos(w0);
        double sinW0 = std::sin(w0);
        double alpha = sinW0 / (2.0 * Q);
        double A = std::pow(10.0, gainDB / 40.0);
        
        switch (type)
        {
            case LOWPASS:
                b1 = 2.0 * (1.0 - cosW0) / (2.0 * (1.0 + alpha));
                b2 = (1.0 - alpha - cosW0) / (1.0 + alpha);
                a0 = (1.0 + cosW0 - alpha) / (2.0 * (1.0 + alpha));
                a1 = 2.0 * (cosW0 - alpha) / (1.0 + alpha);
                a2 = (1.0 + cosW0 + alpha) / (2.0 * (1.0 + alpha));
                break;
            
            case HIGHPASS:
                b1 = -2.0 * (1.0 + cosW0) / (2.0 * (1.0 + alpha));
                b2 = (1.0 + alpha + cosW0) / (1.0 + alpha);
                a0 = (1.0 - cosW0 + alpha) / (2.0 * (1.0 + alpha));
                a1 = -2.0 * (cosW0 + alpha) / (1.0 + alpha);
                a2 = (1.0 - cosW0 - alpha) / (2.0 * (1.0 + alpha));
                break;
            
            case BANDPASS:
                b1 = sinW0 / (1.0 + alpha);
                b2 = 0.0;
                a0 = alpha / (1.0 + alpha);
                a1 = 0.0;
                a2 = -alpha / (1.0 + alpha);
                break;
            
            default:
                // Fallback to lowpass
                b1 = 2.0 * (1.0 - cosW0) / (2.0 * (1.0 + alpha));
                b2 = (1.0 - alpha - cosW0) / (1.0 + alpha);
                a0 = (1.0 + cosW0 - alpha) / (2.0 * (1.0 + alpha));
                a1 = 2.0 * (cosW0 - alpha) / (1.0 + alpha);
                a2 = (1.0 + cosW0 + alpha) / (2.0 * (1.0 + alpha));
        }
        
        // Normalize
        double norm = 1.0 / a0;
        a0 = 1.0;
        a1 *= -norm;
        a2 *= -norm;
        b1 *= norm;
        b2 *= norm;
    }
    
    float BiquadFilter::process(float input)
    {
        float output = a0 * input + a1 * x1 + a2 * x2 - b1 * y1 - b2 * y2;
        
        // Update state
        x2 = x1;
        x1 = input;
        y2 = y1;
        y1 = output;
        
        return denormalPrevent(output);
    }
    
    void BiquadFilter::processBlock(const float* input, float* output, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            output[i] = process(input[i]);
        }
    }
    
    void BiquadFilter::reset()
    {
        x1 = x2 = y1 = y2 = 0.0f;
    }
    
    // ============================================================================
    // CombFilter Implementation
    // ============================================================================
    
    CombFilter::CombFilter(double delayMs, float feedback, double sampleRate)
        : feedback(clamp(feedback, 0.0f, 0.99f))
    {
        delayLine = new DelayLine(delayMs / 1000.0, sampleRate);
        delayLine->setDelayMs(delayMs);
    }
    
    CombFilter::~CombFilter()
    {
        delete delayLine;
    }
    
    void CombFilter::setSampleRate(double sampleRate)
    {
        delayLine->setSampleRate(sampleRate);
    }
    
    void CombFilter::setDelay(double delayMs)
    {
        delayLine->setDelayMs(delayMs);
    }
    
    void CombFilter::setFeedback(float feedback)
    {
        this->feedback = clamp(feedback, 0.0f, 0.99f);
    }
    
    float CombFilter::process(float input)
    {
        float delayed = delayLine->read();
        float output = input + feedback * delayed;
        delayLine->process(output);
        return output;
    }
    
    void CombFilter::reset()
    {
        delayLine->reset();
    }
    
    // ============================================================================
    // AllpassFilter Implementation
    // ============================================================================
    
    AllpassFilter::AllpassFilter(double delayMs, float feedback, double sampleRate)
        : feedback(clamp(feedback, 0.0f, 0.99f))
    {
        delayLine = new DelayLine(delayMs / 1000.0, sampleRate);
        delayLine->setDelayMs(delayMs);
    }
    
    AllpassFilter::~AllpassFilter()
    {
        delete delayLine;
    }
    
    void AllpassFilter::setSampleRate(double sampleRate)
    {
        delayLine->setSampleRate(sampleRate);
    }
    
    void AllpassFilter::setDelay(double delayMs)
    {
        delayLine->setDelayMs(delayMs);
    }
    
    void AllpassFilter::setFeedback(float feedback)
    {
        this->feedback = clamp(feedback, 0.0f, 0.99f);
    }
    
    float AllpassFilter::process(float input)
    {
        float delayed = delayLine->read();
        float output = -input + feedback * delayed;
        delayLine->process(input + feedback * output);
        return output;
    }
    
    void AllpassFilter::reset()
    {
        delayLine->reset();
    }
    
    // ============================================================================
    // LFO Implementation
    // ============================================================================
    
    LFO::LFO(double rate, double depth, double sampleRate, Waveform waveform)
        : sampleRate(sampleRate),
          rate(clamp(rate, 0.01, 20.0)),
          depth(clamp(depth, 0.0, 1.0)),
          offset(0.0),
          waveform(waveform),
          phase(0.0),
          randomPhase(0.0),
          randomRate(1.0),
          randomValue(0.0f)
    {
    }
    
    LFO::~LFO()
    {
    }
    
    void LFO::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
    }
    
    void LFO::setRate(double rate)
    {
        this->rate = clamp(rate, 0.01, 20.0);
    }
    
    void LFO::setDepth(double depth)
    {
        this->depth = clamp(depth, 0.0, 1.0);
    }
    
    void LFO::setWaveform(Waveform waveform)
    {
        this->waveform = waveform;
    }
    
    void LFO::setOffset(double offset)
    {
        this->offset = clamp(offset, -1.0, 1.0);
    }
    
    float LFO::getValue()
    {
        float value = 0.0f;
        
        switch (waveform)
        {
            case SINE:
                value = static_cast<float>(std::sin(phase * TWO_PI));
                break;
            case TRIANGLE:
                value = static_cast<float>(2.0 * std::abs(2.0 * (phase - std::floor(phase + 0.5))) - 1.0);
                break;
            case SQUARE:
                value = phase < 0.5f ? 1.0f : -1.0f;
                break;
            case RANDOM:
                if (phase >= randomPhase)
                {
                    randomValue = rng.nextFloat() * 2.0f - 1.0f; // -1 to 1
                    randomPhase = phase + 1.0 / randomRate;
                }
                value = randomValue;
                break;
        }
        
        // Apply depth and offset
        float result = value * static_cast<float>(depth) + static_cast<float>(offset);
        
        // Update phase
        phase += rate / sampleRate;
        if (phase >= 1.0)
            phase -= 1.0;
        
        return result;
    }
    
    void LFO::processBlock(float* output, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            output[i] = getValue();
        }
    }
    
    void LFO::reset()
    {
        phase = 0.0;
        randomPhase = 0.0;
        randomValue = 0.0f;
    }
    
    // ============================================================================
    // SmoothedParameter Implementation
    // ============================================================================
    
    SmoothedParameter::SmoothedParameter(float initialValue, float minValue, float maxValue,
                                         double smoothingTimeMs, double sampleRate)
        : minValue(minValue),
          maxValue(maxValue),
          smoothingTimeMs(smoothingTimeMs),
          sampleRate(sampleRate),
          targetValue(clamp(initialValue, minValue, maxValue)),
          currentValue(targetValue)
    {
        updateAlpha();
    }
    
    SmoothedParameter::~SmoothedParameter()
    {
    }
    
    void SmoothedParameter::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        updateAlpha();
    }
    
    void SmoothedParameter::setSmoothingTime(double smoothingTimeMs)
    {
        this->smoothingTimeMs = smoothingTimeMs;
        updateAlpha();
    }
    
    void SmoothedParameter::setRange(float minValue, float maxValue)
    {
        this->minValue = minValue;
        this->maxValue = maxValue;
        targetValue = clamp(targetValue, minValue, maxValue);
        currentValue = clamp(currentValue, minValue, maxValue);
    }
    
    void SmoothedParameter::setTarget(float value)
    {
        targetValue = clamp(value, minValue, maxValue);
    }
    
    float SmoothedParameter::getValue() const
    {
        return currentValue;
    }
    
    float SmoothedParameter::getTarget() const
    {
        return targetValue;
    }
    
    void SmoothedParameter::processSample()
    {
        currentValue = alpha * targetValue + (1.0f - alpha) * currentValue;
    }
    
    void SmoothedParameter::processBlock(int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            processSample();
        }
    }
    
    void SmoothedParameter::reset()
    {
        currentValue = targetValue;
    }
    
    void SmoothedParameter::updateAlpha()
    {
        if (sampleRate <= 0 || smoothingTimeMs <= 0)
        {
            alpha = 1.0f; // No smoothing
        }
        else
        {
            // alpha = 1 - exp(-1 / (smoothingTime * sampleRate))
            alpha = static_cast<float>(1.0 - std::exp(-1.0 / (smoothingTimeMs * 0.001 * sampleRate)));
        }
    }
    
    // ============================================================================
    // ParameterSystem Implementation
    // ============================================================================
    
    ParameterSystem::ParameterSystem(double sampleRate)
        : sampleRate(sampleRate)
    {
    }
    
    ParameterSystem::~ParameterSystem()
    {
    }
    
    void ParameterSystem::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        for (int i = 0; i < parameters.size(); ++i)
        {
            parameters[i]->setSampleRate(sampleRate);
        }
    }
    
    void ParameterSystem::addParameter(const juce::String& id, float initialValue,
                                         float minValue, float maxValue, double smoothingTimeMs,
                                         bool logarithmic)
    {
        juce::ScopedLock sl(lock);
        parameters.add(new SmoothedParameter(initialValue, minValue, maxValue, smoothingTimeMs, sampleRate));
        parameterIDs.add(id);
    }
    
    void ParameterSystem::setParameter(const juce::String& id, float value)
    {
        juce::ScopedLock sl(lock);
        int index = parameterIDs.indexOf(id);
        if (index >= 0 && index < parameters.size())
        {
            parameters[index]->setTarget(value);
        }
    }
    
    float ParameterSystem::getParameter(const juce::String& id) const
    {
        juce::ScopedLock sl(lock);
        int index = parameterIDs.indexOf(id);
        if (index >= 0 && index < parameters.size())
        {
            return parameters[index]->getValue();
        }
        return 0.0f;
    }
    
    float ParameterSystem::getSmoothedParameter(const juce::String& id)
    {
        juce::ScopedLock sl(lock);
        int index = parameterIDs.indexOf(id);
        if (index >= 0 && index < parameters.size())
        {
            parameters[index]->processSample();
            return parameters[index]->getValue();
        }
        return 0.0f;
    }
    
    void ParameterSystem::processBlock(int numSamples)
    {
        juce::ScopedLock sl(lock);
        for (int i = 0; i < parameters.size(); ++i)
        {
            parameters[i]->processBlock(numSamples);
        }
    }
    
    void ParameterSystem::reset()
    {
        juce::ScopedLock sl(lock);
        for (int i = 0; i < parameters.size(); ++i)
        {
            parameters[i]->reset();
        }
    }
    
    juce::StringArray ParameterSystem::getParameterIDs() const
    {
        juce::ScopedLock sl(lock);
        return parameterIDs;
    }
