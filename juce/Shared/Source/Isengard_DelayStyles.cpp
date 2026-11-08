/**
 * Isengard Delay Styles Implementation
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#include "Isengard_DelayStyles.h"
#include "Isengard_DelayModes.h"

namespace Isengard
{
    // ============================================================================
    // DelayStyleBase Implementation
    // ============================================================================
    
    DelayStyleBase::DelayStyleBase(double sampleRate)
        : sampleRate(sampleRate),
          modeProcessor(nullptr),
          spread(0.5f),
          ratio(0.5f),
          delayLineL(nullptr),
          delayLineR(nullptr)
    {
        delayLineL = new DelayLine(5.0, sampleRate);
        delayLineR = new DelayLine(5.0, sampleRate);
        initializeDefaultParameters();
    }
    
    DelayStyleBase::~DelayStyleBase()
    {
        delete delayLineL;
        delete delayLineR;
    }
    
    float DelayStyleBase::process(float input)
    {
        // Default: pass through
        return input;
    }
    
    std::pair<float, float> DelayStyleBase::process(float leftInput, float rightInput)
    {
        return {leftInput, rightInput};
    }
    
    void DelayStyleBase::processBlock(const float* inputL, const float* inputR, float* outputL, float* outputR, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            auto [outL, outR] = process(inputL[i], inputR[i]);
            outputL[i] = outL;
            outputR[i] = outR;
        }
    }
    
    void DelayStyleBase::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        if (delayLineL) delayLineL->setSampleRate(sampleRate);
        if (delayLineR) delayLineR->setSampleRate(sampleRate);
    }
    
    void DelayStyleBase::setParameter(const juce::String& paramName, float value)
    {
        if (paramName == "spread") spread = clamp(value, 0.0f, 1.0f);
        else if (paramName == "ratio") ratio = clamp(value, 0.0f, 1.0f);
        else if (paramName == "delay_time_l_ms") 
        {
            if (delayLineL) delayLineL->setDelayMs(value);
        }
        else if (paramName == "delay_time_r_ms") 
        {
            if (delayLineR) delayLineR->setDelayMs(value);
        }
    }
    
    void DelayStyleBase::setModeProcessor(DelayModeBase* mode)
    {
        modeProcessor = mode;
    }
    
    void DelayStyleBase::reset()
    {
        if (delayLineL) delayLineL->reset();
        if (delayLineR) delayLineR->reset();
    }
    
    void DelayStyleBase::initializeDefaultParameters()
    {
        spread = 0.5f;
        ratio = 0.5f;
    }
    
    // ============================================================================
    // SingleStyle Implementation
    // ============================================================================
    
    SingleStyle::SingleStyle(double sampleRate)
        : DelayStyleBase(sampleRate)
    {
    }
    
    SingleStyle::~SingleStyle()
    {
    }
    
    float SingleStyle::process(float input)
    {
        // Single mode: process through delay line L (mono)
        if (modeProcessor)
        {
            return modeProcessor->process(input);
        }
        return input;
    }
    
    std::pair<float, float> SingleStyle::process(float leftInput, float rightInput)
    {
        // Both channels get the same processed signal
        float processed = process(leftInput);
        return {processed, processed};
    }
    
    void SingleStyle::processBlock(const float* inputL, const float* inputR, float* outputL, float* outputR, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            float processed = process(inputL[i]);
            outputL[i] = processed;
            outputR[i] = processed;
        }
    }
    
    void SingleStyle::setSampleRate(double sampleRate)
    {
        DelayStyleBase::setSampleRate(sampleRate);
    }
    
    void SingleStyle::setParameter(const juce::String& paramName, float value)
    {
        DelayStyleBase::setParameter(paramName, value);
    }
    
    void SingleStyle::setModeProcessor(DelayModeBase* mode)
    {
        DelayStyleBase::setModeProcessor(mode);
    }
    
    void SingleStyle::reset()
    {
        DelayStyleBase::reset();
    }
    
    // ============================================================================
    // DualStyle Implementation
    // ============================================================================
    
    DualStyle::DualStyle(double sampleRate)
        : DelayStyleBase(sampleRate),
          delayTimeLMs(500.0f),
          delayTimeRMs(500.0f)
    {
        if (delayLineL) delayLineL->setDelayMs(delayTimeLMs);
        if (delayLineR) delayLineR->setDelayMs(delayTimeRMs);
    }
    
    DualStyle::~DualStyle()
    {
    }
    
    float DualStyle::process(float input)
    {
        return input;
    }
    
    std::pair<float, float> DualStyle::process(float leftInput, float rightInput)
    {
        // Process each channel independently
        float outL = delayLineL->process(leftInput);
        float outR = delayLineR->process(rightInput);
        return {outL, outR};
    }
    
    void DualStyle::processBlock(const float* inputL, const float* inputR, float* outputL, float* outputR, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            auto [outL, outR] = process(inputL[i], inputR[i]);
            outputL[i] = outL;
            outputR[i] = outR;
        }
    }
    
    void DualStyle::setSampleRate(double sampleRate)
    {
        DelayStyleBase::setSampleRate(sampleRate);
    }
    
    void DualStyle::setParameter(const juce::String& paramName, float value)
    {
        DelayStyleBase::setParameter(paramName, value);
        if (paramName == "delay_time_l_ms") delayTimeLMs = value;
        else if (paramName == "delay_time_r_ms") delayTimeRMs = value;
    }
    
    void DualStyle::setModeProcessor(DelayModeBase* mode)
    {
        DelayStyleBase::setModeProcessor(mode);
    }
    
    void DualStyle::reset()
    {
        DelayStyleBase::reset();
    }
    
    // ============================================================================
    // RatioStyle Implementation
    // ============================================================================
    
    RatioStyle::RatioStyle(double sampleRate)
        : DelayStyleBase(sampleRate)
    {
    }
    
    RatioStyle::~RatioStyle()
    {
    }
    
    float RatioStyle::process(float input)
    {
        return input;
    }
    
    std::pair<float, float> RatioStyle::process(float leftInput, float rightInput)
    {
        // Right delay is ratio of left delay
        float leftDelay = delayLineL->getDelayTime() * 1000.0f; // Convert to ms
        float rightDelay = leftDelay * (0.5f + ratio); // Ratio-based
        delayLineR->setDelayMs(clamp(rightDelay, 1.0f, 5000.0f));
        
        float outL = delayLineL->process(leftInput);
        float outR = delayLineR->process(rightInput);
        return {outL, outR};
    }
    
    void RatioStyle::processBlock(const float* inputL, const float* inputR, float* outputL, float* outputR, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            auto [outL, outR] = process(inputL[i], inputR[i]);
            outputL[i] = outL;
            outputR[i] = outR;
        }
    }
    
    void RatioStyle::setSampleRate(double sampleRate)
    {
        DelayStyleBase::setSampleRate(sampleRate);
    }
    
    void RatioStyle::setParameter(const juce::String& paramName, float value)
    {
        DelayStyleBase::setParameter(paramName, value);
        if (paramName == "ratio") ratio = value;
    }
    
    void RatioStyle::setModeProcessor(DelayModeBase* mode)
    {
        DelayStyleBase::setModeProcessor(mode);
    }
    
    void RatioStyle::reset()
    {
        DelayStyleBase::reset();
    }
    
    // ============================================================================
    // PingPongStyle Implementation
    // ============================================================================
    
    PingPongStyle::PingPongStyle(double sampleRate)
        : DelayStyleBase(sampleRate),
          pingPongDirection(true)
    {
    }
    
    PingPongStyle::~PingPongStyle()
    {
    }
    
    float PingPongStyle::process(float input)
    {
        return input;
    }
    
    std::pair<float, float> PingPongStyle::process(float leftInput, float rightInput)
    {
        // PingPong: delay bounces between channels
        float outL, outR;
        
        if (pingPongDirection)
        {
            // L -> R
            outL = leftInput;
            outR = delayLineL->process(leftInput);
        }
        else
        {
            // R -> L
            outR = rightInput;
            outL = delayLineR->process(rightInput);
        }
        
        // Toggle direction
        pingPongDirection = !pingPongDirection;
        
        return {outL, outR};
    }
    
    void PingPongStyle::processBlock(const float* inputL, const float* inputR, float* outputL, float* outputR, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            auto [outL, outR] = process(inputL[i], inputR[i]);
            outputL[i] = outL;
            outputR[i] = outR;
        }
    }
    
    void PingPongStyle::setSampleRate(double sampleRate)
    {
        DelayStyleBase::setSampleRate(sampleRate);
    }
    
    void PingPongStyle::setParameter(const juce::String& paramName, float value)
    {
        DelayStyleBase::setParameter(paramName, value);
    }
    
    void PingPongStyle::setModeProcessor(DelayModeBase* mode)
    {
        DelayStyleBase::setModeProcessor(mode);
    }
    
    void PingPongStyle::reset()
    {
        DelayStyleBase::reset();
        pingPongDirection = true;
    }
    
    // ============================================================================
    // QuadStyle Implementation
    // ============================================================================
    
    QuadStyle::QuadStyle(double sampleRate)
        : DelayStyleBase(sampleRate),
          delayLineL1(nullptr),
          delayLineL2(nullptr),
          delayLineR1(nullptr),
          delayLineR2(nullptr)
    {
        delayLineL1 = new DelayLine(5.0, sampleRate);
        delayLineL2 = new DelayLine(5.0, sampleRate);
        delayLineR1 = new DelayLine(5.0, sampleRate);
        delayLineR2 = new DelayLine(5.0, sampleRate);
        
        // Set different delay times for each tap
        delayLineL1->setDelayMs(250.0f);
        delayLineL2->setDelayMs(500.0f);
        delayLineR1->setDelayMs(375.0f);
        delayLineR2->setDelayMs(750.0f);
    }
    
    QuadStyle::~QuadStyle()
    {
        delete delayLineL1;
        delete delayLineL2;
        delete delayLineR1;
        delete delayLineR2;
    }
    
    float QuadStyle::process(float input)
    {
        return input;
    }
    
    std::pair<float, float> QuadStyle::process(float leftInput, float rightInput)
    {
        // Quad: four taps with spread
        float tapL1 = delayLineL1->process(leftInput);
        float tapL2 = delayLineL2->process(leftInput);
        float tapR1 = delayLineR1->process(rightInput);
        float tapR2 = delayLineR2->process(rightInput);
        
        // Mix taps with spread
        float outL = (tapL1 + tapR1) * 0.5f;
        float outR = (tapL2 + tapR2) * 0.5f;
        
        // Apply spread
        outL = outL * (0.5f + spread * 0.5f);
        outR = outR * (0.5f + spread * 0.5f);
        
        return {outL, outR};
    }
    
    void QuadStyle::processBlock(const float* inputL, const float* inputR, float* outputL, float* outputR, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            auto [outL, outR] = process(inputL[i], inputR[i]);
            outputL[i] = outL;
            outputR[i] = outR;
        }
    }
    
    void QuadStyle::setSampleRate(double sampleRate)
    {
        DelayStyleBase::setSampleRate(sampleRate);
        if (delayLineL1) delayLineL1->setSampleRate(sampleRate);
        if (delayLineL2) delayLineL2->setSampleRate(sampleRate);
        if (delayLineR1) delayLineR1->setSampleRate(sampleRate);
        if (delayLineR2) delayLineR2->setSampleRate(sampleRate);
    }
    
    void QuadStyle::setParameter(const juce::String& paramName, float value)
    {
        DelayStyleBase::setParameter(paramName, value);
    }
    
    void QuadStyle::setModeProcessor(DelayModeBase* mode)
    {
        DelayStyleBase::setModeProcessor(mode);
    }
    
    void QuadStyle::reset()
    {
        DelayStyleBase::reset();
        if (delayLineL1) delayLineL1->reset();
        if (delayLineL2) delayLineL2->reset();
        if (delayLineR1) delayLineR1->reset();
        if (delayLineR2) delayLineR2->reset();
    }
}
