/**
 * Wow and Flutter LFO for Tape Mode
 * 
 * Specialized LFO for emulating tape wow and flutter characteristics.
 * Based on ValhallaDelay evidence E012.
 * 
 * Characteristics:
 * - Wow: Slow random modulation (0.1-2 Hz)
 * - Flutter: Fast random modulation (2-20 Hz)
 * - Rates are functions of delay time: Wow rate = 1000ms / delayTimeMs, Flutter rate = Wow rate * 10
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#pragma once

#include <JuceHeader.h>
#include "Isengard_DSP.h"

namespace Isengard
{
    /**
     * Wow and Flutter LFO for tape delay emulation.
     * 
     * Generates two synchronized random LFOs for wow (slow) and flutter (fast) modulation.
     */
    class WowFlutterLFO
    {
    public:
        WowFlutterLFO(double sampleRate, double delayTimeMs = 500.0);
        ~WowFlutterLFO();
        
        // Set sample rate
        void setSampleRate(double sampleRate);
        
        // Set delay time and update rates
        void setDelayTime(double delayTimeMs);
        
        // Set wow depth (0.0 to 1.0)
        void setWowDepth(float depth);
        
        // Set flutter depth (0.0 to 1.0)
        void setFlutterDepth(float depth);
        
        // Get combined wow + flutter value
        float getValue();
        
        // Get separate wow and flutter values
        std::pair<float, float> getValues();
        
        // Process one sample (advance both LFOs)
        void processSample();
        
        // Process a block of samples
        void processBlock(int numSamples);
        
        // Reset the LFOs
        void reset();
        
    private:
        double sampleRate;
        double delayTimeMs;
        
        // Wow and flutter LFOs
        LFO* wowLFO;
        LFO* flutterLFO;
        
        // Current values
        float currentWowValue;
        float currentFlutterValue;
        
        // Update wow and flutter rates based on delay time
        void updateRates();
        
        JUCE_DECLARE_NON_COPYABLE(WowFlutterLFO)
    };
}
