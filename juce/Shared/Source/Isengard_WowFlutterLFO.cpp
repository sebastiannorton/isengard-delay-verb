/**
 * Wow and Flutter LFO Implementation
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#include "Isengard_WowFlutterLFO.h"
#include "Isengard_DSP.h"

namespace Isengard
{
    WowFlutterLFO::WowFlutterLFO(double sampleRate, double delayTimeMs)
        : sampleRate(sampleRate),
          delayTimeMs(delayTimeMs),
          wowLFO(nullptr),
          flutterLFO(nullptr),
          currentWowValue(0.0f),
          currentFlutterValue(0.0f)
    {
        // Create wow LFO (slow random modulation)
        wowLFO = new LFO(1.0, 0.1f, sampleRate, LFO::RANDOM);
        
        // Create flutter LFO (fast random modulation)
        flutterLFO = new LFO(10.0, 0.05f, sampleRate, LFO::RANDOM);
        
        // Update rates based on delay time
        updateRates();
    }
    
    WowFlutterLFO::~WowFlutterLFO()
    {
        delete wowLFO;
        delete flutterLFO;
    }
    
    void WowFlutterLFO::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        if (wowLFO) wowLFO->setSampleRate(sampleRate);
        if (flutterLFO) flutterLFO->setSampleRate(sampleRate);
    }
    
    void WowFlutterLFO::setDelayTime(double delayTimeMs)
    {
        this->delayTimeMs = delayTimeMs;
        updateRates();
    }
    
    void WowFlutterLFO::setWowDepth(float depth)
    {
        if (wowLFO) wowLFO->setDepth(clamp(depth, 0.0f, 1.0f));
    }
    
    void WowFlutterLFO::setFlutterDepth(float depth)
    {
        if (flutterLFO) flutterLFO->setDepth(clamp(depth, 0.0f, 1.0f));
    }
    
    float WowFlutterLFO::getValue()
    {
        return currentWowValue + currentFlutterValue;
    }
    
    std::pair<float, float> WowFlutterLFO::getValues()
    {
        return {currentWowValue, currentFlutterValue};
    }
    
    void WowFlutterLFO::processSample()
    {
        if (wowLFO)
        {
            currentWowValue = wowLFO->getValue();
            wowLFO->processBlock(&currentWowValue, 1);
        }
        
        if (flutterLFO)
        {
            currentFlutterValue = flutterLFO->getValue();
            flutterLFO->processBlock(&currentFlutterValue, 1);
        }
    }
    
    void WowFlutterLFO::processBlock(int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            processSample();
        }
    }
    
    void WowFlutterLFO::reset()
    {
        if (wowLFO) wowLFO->reset();
        if (flutterLFO) flutterLFO->reset();
        currentWowValue = 0.0f;
        currentFlutterValue = 0.0f;
    }
    
    void WowFlutterLFO::updateRates()
    {
        if (delayTimeMs <= 0) return;
        
        // Wow rate: 1000ms / delayTimeMs (clamped to 0.1-2Hz)
        // Evidence E012: Wow/Flutter rates are functions of delay time
        double wowRate = 1000.0 / delayTimeMs;
        wowRate = clamp(static_cast<float>(wowRate), 0.1f, 2.0f);
        if (wowLFO) wowLFO->setRate(wowRate);
        
        // Flutter rate: Wow rate * 10 (2-20Hz)
        double flutterRate = wowRate * 10.0;
        flutterRate = clamp(static_cast<float>(flutterRate), 2.0f, 20.0f);
        if (flutterLFO) flutterLFO->setRate(static_cast<float>(flutterRate));
    }
}
