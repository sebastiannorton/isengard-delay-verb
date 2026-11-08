/**
 * Isengard Delay Processor
 * 
 * Unified delay processor combining mode, style, and parameter handling.
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#pragma once

#include <JuceHeader.h>
#include "Isengard_DSP.h"

namespace Isengard
{
    // Forward declarations
    class DelayModeBase;
    class DelayStyleBase;
    class SmoothedParameter;
    
    /**
     * Unified delay processor for Isengard Delay.
     * 
     * Combines mode and style into a single processing chain:
     * 1. Input filtering
     * 2. Mode processing (delay line, modulation, effects)
     * 3. Style routing (stereo handling)
     * 4. Output filtering
     * 5. Dry/wet mix
     */
    class DelayProcessor
    {
    public:
        /**
         * Delay modes
         */
        enum Mode
        {
            MODE_TAPE = 0,
            MODE_HIFI,
            MODE_BBD,
            MODE_DIGITAL,
            MODE_GHOST,
            MODE_PITCH,
            MODE_REVPITCH,
            NUM_MODES
        };
        
        /**
         * Delay styles
         */
        enum Style
        {
            STYLE_SINGLE = 0,
            STYLE_DUAL,
            STYLE_RATIO,
            STYLE_PINGPONG,
            STYLE_QUAD,
            NUM_STYLES
        };
        
        // Constructor/Destructor
        DelayProcessor(double sampleRate);
        ~DelayProcessor();
        
        // Set sample rate
        void setSampleRate(double sampleRate);
        
        // Set mode
        void setMode(Mode mode);
        void setMode(const juce::String& modeName);
        
        // Set style
        void setStyle(Style style);
        void setStyle(const juce::String& styleName);
        
        // Set parameters
        void setParameters(const std::map<juce::String, float>& params);
        void setParameter(const juce::String& paramName, float value);
        
        // Process a single sample (mono)
        float processSample(float input);
        
        // Process a stereo sample
        std::pair<float, float> processSample(float leftInput, float rightInput);
        
        // Process a block of samples
        void processBlock(const float* inputL, const float* inputR, float* outputL, float* outputR, int numSamples);
        
        // Reset the processor
        void reset();
        
        // Get current mode and style
        Mode getMode() const { return currentMode; }
        Style getStyle() const { return currentStyle; }
        
    private:
        double sampleRate;
        Mode currentMode;
        Style currentStyle;
        
        // DSP Components
        DelayModeBase* modeProcessor;
        DelayStyleBase* styleProcessor;
        
        // Input/Output filters
        OnePoleFilter* inputHighpass;
        OnePoleFilter* inputLowpass;
        OnePoleFilter* outputHighpass;
        OnePoleFilter* outputLowpass;
        OnePoleFilter* eqHigh;
        OnePoleFilter* eqLow;
        
        // Smoothed parameters
        std::map<juce::String, SmoothedParameter*> smoothers;
        
        // Parameter values
        std::map<juce::String, float> params;
        
        // Create mode processor
        DelayModeBase* createModeProcessor(Mode mode);
        
        // Create style processor
        DelayStyleBase* createStyleProcessor(Style style);
        
        // Create smoothed parameter
        SmoothedParameter* createSmoothedParameter(
            const juce::String& name, 
            float defaultValue, 
            float minValue, 
            float maxValue,
            float smoothTimeMs = 10.0f
        );
        
        // Initialize smoothers
        void initializeSmoothers();
        
        // Initialize default parameters
        void initializeDefaultParameters();
        
        JUCE_DECLARE_NON_COPYABLE(DelayProcessor)
    };
    
    // ============================================================================
    // Smoothed Parameter
    // ============================================================================
    
    /**
     * Smoothed parameter for click-free automation.
     */
    class SmoothedParameter
    {
    public:
        SmoothedParameter(float initialValue, float minValue, float maxValue, 
                         float smoothTimeMs, double sampleRate);
        ~SmoothedParameter();
        
        // Set target value
        void setValue(float value);
        
        // Get current smoothed value
        float getValue() const;
        
        // Process one sample
        float process();
        
        // Set sample rate
        void setSampleRate(double sampleRate);
        
        // Set smooth time
        void setSmoothTime(float smoothTimeMs);
        
        // Reset to initial value
        void reset();
        
    private:
        float currentValue;
        float targetValue;
        float minValue;
        float maxValue;
        float smoothTimeMs;
        double sampleRate;
        float coefficient;
        
        void updateCoefficient();
        
        JUCE_DECLARE_NON_COPYABLE(SmoothedParameter)
    };
}
