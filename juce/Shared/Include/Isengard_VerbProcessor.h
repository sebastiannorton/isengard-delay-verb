/**
 * Isengard Verb Processor
 * 
 * Unified reverb processor combining mode, color, and parameter handling.
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#pragma once

#include <JuceHeader.h>
#include "Isengard_DSP.h"
#include "Isengard_FDN.h"

namespace Isengard
{
    // Forward declarations
    class VerbModeBase;
    class ColorSystem;
    class EarlyReflections;
    class ModulationMatrix;
    
    /**
     * Unified reverb processor for Isengard Verb.
     * 
     * Combines mode, color, and processing chain:
     * 1. Input filtering
     * 2. Early reflections
     * 3. FDN reverb
     * 4. Modulation
     * 5. Color processing
     * 6. Output filtering
     * 7. Dry/wet mix
     */
    class VerbProcessor
    {
    public:
        /**
         * Verb modes (22 modes from 1972-1995 + NOW1, NOW2)
         */
        enum Mode
        {
            MODE_1972 = 0,
            MODE_1974,
            MODE_1975,
            MODE_1976,
            MODE_1977,
            MODE_1978,
            MODE_1979,
            MODE_1980,
            MODE_1981,
            MODE_1982,
            MODE_1983,
            MODE_1984,
            MODE_1985,
            MODE_1986,
            MODE_1987,
            MODE_1990,
            MODE_1991,
            MODE_1992,
            MODE_1993,
            MODE_1994,
            MODE_1995,
            MODE_NOW1,
            MODE_NOW2,
            NUM_MODES
        };
        
        /**
         * Color settings
         */
        enum Color
        {
            COLOR_1970S = 0,
            COLOR_1980S,
            COLOR_NOW,
            NUM_COLORS
        };
        
        // Constructor/Destructor
        VerbProcessor(double sampleRate);
        ~VerbProcessor();
        
        // Set sample rate
        void setSampleRate(double sampleRate);
        
        // Set mode
        void setMode(Mode mode);
        void setMode(const juce::String& modeName);
        
        // Set color
        void setColor(Color color);
        void setColor(const juce::String& colorName);
        
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
        
        // Get current mode and color
        Mode getMode() const { return currentMode; }
        Color getColor() const { return currentColor; }
        
    private:
        double sampleRate;
        Mode currentMode;
        Color currentColor;
        
        // DSP Components
        VerbModeBase* modeProcessor;
        ColorSystem* colorSystem;
        EarlyReflections* earlyReflections;
        ModulationMatrix* modulationMatrix;
        
        // FDN Reverb
        FDNReverb* fdnReverb;
        
        // Input/Output filters
        OnePoleFilter* inputHighpass;
        OnePoleFilter* inputLowpass;
        OnePoleFilter* outputHighpass;
        OnePoleFilter* outputLowpass;
        BiquadFilter* highCutFilter;
        BiquadFilter* lowCutFilter;
        
        // Smoothed parameters
        std::map<juce::String, float> params;
        
        // Create mode processor
        VerbModeBase* createModeProcessor(Mode mode);
        
        // Create color system
        ColorSystem* createColorSystem(Color color);
        
        // Initialize default parameters
        void initializeDefaultParameters();
        
        JUCE_DECLARE_NON_COPYABLE(VerbProcessor)
    };
    
    // ============================================================================
    // Verb Mode Base Class
    // ============================================================================
    
    /**
     * Base class for all verb modes.
     * 
     * Each mode configures the FDN reverb with specific parameters
     * for a particular vintage reverb sound.
     */
    class VerbModeBase
    {
    public:
        VerbModeBase(double sampleRate);
        virtual ~VerbModeBase();
        
        virtual void configureFDN(FDNReverb* fdn) = 0;
        virtual void configureEarlyReflections(EarlyReflections* er) = 0;
        virtual void configureModulation(ModulationMatrix* mod) = 0;
        
        virtual void setSampleRate(double sampleRate);
        virtual void setParameter(const juce::String& paramName, float value);
        virtual void reset();
        
        virtual juce::String getName() const = 0;
        
    protected:
        double sampleRate;
    };
    
    // ============================================================================
    // Color System
    // ============================================================================
    
    /**
     * Color system for verb processing.
     * 
     * Applies color-specific EQ and character to the reverb sound.
     */
    class ColorSystem
    {
    public:
        enum ColorType { COLOR_1970S, COLOR_1980S, COLOR_NOW };
        
        ColorSystem(double sampleRate, ColorType color);
        ~ColorSystem();
        
        void setSampleRate(double sampleRate);
        void setColor(ColorType color);
        
        float process(float input);
        void processBlock(const float* input, float* output, int numSamples);
        void reset();
        
    private:
        double sampleRate;
        ColorType color;
        
        OnePoleFilter* dampingFilter;
        BiquadFilter* toneFilter;
        
        float dampingAmount;
        float toneAmount;
    };
}
