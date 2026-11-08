/**
 * Isengard FDN - Feedback Delay Network Reverb
 * 
 * This header provides the FDN reverb implementation for Isengard Verb.
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#pragma once

#include "Isengard_DSP.h"

namespace Isengard
{
    /**
     * Feedback Delay Network (FDN) Reverb.
     * 
     * This implements a classic FDN reverb with:
     * - 4 comb filters for late reverberation
     * - 2 allpass filters for diffusion
     * - Orthogonal feedback matrix for stability
     * - Damping filters for frequency-dependent decay
     * - Modulation network for temporal variation
     */
    class FDNReverb
    {
    public:
        FDNReverb(double sampleRate);
        ~FDNReverb();
        
        // Set sample rate
        void setSampleRate(double sampleRate);
        
        // Set parameters
        void setDecay(float decay);
        void setSize(float size);
        void setDamping(float damping);
        void setDampingFreq(float freq);
        void setDiffusion(float diffusion);
        void setModRate(float rate);
        void setModDepth(float depth);
        void setPreDelay(float preDelayMs);
        
        // Set all parameters at once
        void setParameters(const juce::NamedValueSet& params);
        
        // Process a single sample
        float processSample(float input);
        
        // Process a block of samples
        void processBlock(const float* input, float* output, int numSamples);
        
        // Reset
        void reset();
        
        // Set comb filter configuration
        void setCombDelays(const float* delaysMs, int numDelays);
        void setCombFeedbacks(const float* feedbacks, int numFeedbacks);
        
        // Set allpass filter configuration
        void setAllpassDelays(const float* delaysMs, int numDelays);
        void setAllpassFeedbacks(const float* feedbacks, int numFeedbacks);
        
    private:
        double sampleRate;
        
        // Comb filters
        juce::OwnedArray<CombFilter> combFilters;
        juce::Array<float> combDelaysMs;
        juce::Array<float> combFeedbacks;
        juce::OwnedArray<OnePoleFilter> dampingFilters;
        
        // Allpass filters
        juce::OwnedArray<AllpassFilter> allpassFilters;
        juce::Array<float> allpassDelaysMs;
        juce::Array<float> allpassFeedbacks;
        
        // Feedback matrix (4x4)
        float feedbackMatrix[4][4];
        
        // Input/output diffusion
        AllpassFilter* inputDiffusion;
        AllpassFilter* outputDiffusion;
        
        // Modulation
        juce::OwnedArray<LFO> combLFOs;
        juce::OwnedArray<LFO> allpassLFOs;
        LFO* globalLFO;
        
        // Parameters
        float decay;
        float size;
        float damping;
        float dampingFreq;
        float diffusion;
        float modRate;
        float modDepth;
        float preDelayMs;
        
        // Create orthogonal matrix
        void createOrthogonalMatrix();
        
        // Update comb filter parameters
        void updateCombFilters();
        
        // Update allpass filter parameters
        void updateAllpassFilters();
        
        // Update damping filters
        void updateDampingFilters();
        
        // Update modulation
        void updateModulation();
        
        JUCE_DECLARE_NON_COPYABLE(FDNReverb)
    };
    
    // ============================================================================
    // Early Reflections
    // ============================================================================
    
    /**
     * Early reflection generator.
     */
    class EarlyReflections
    {
    public:
        struct Tap
        {
            float delayMs;
            float gainL;
            float gainR;
        };
        
        EarlyReflections(double sampleRate);
        ~EarlyReflections();
        
        void setSampleRate(double sampleRate);
        
        // Set parameters
        void setSize(float size);
        void setWidth(float width);
        void setPreDelay(float preDelayMs);
        void setEarlyLevel(float level);
        
        // Set taps
        void setTaps(const juce::Array<Tap>& taps);
        
        // Set mode (loads mode-specific taps)
        void setMode(const juce::String& mode);
        
        // Process a sample pair
        void processSample(float inputL, float inputR, float* outputL, float* outputR);
        
        // Process a block
        void processBlock(const float* inputL, const float* inputR, 
                          float* outputL, float* outputR, int numSamples);
        
        void reset();
        
    private:
        double sampleRate;
        
        // Parameters
        float size;
        float width;
        float preDelayMs;
        float earlyLevel;
        
        // Pre-delay line
        DelayLine* preDelayLine;
        
        // Tap delays
        juce::OwnedArray<DelayLine> tapDelaysL;
        juce::OwnedArray<DelayLine> tapDelaysR;
        juce::Array<Tap> taps;
        
        // Damping filter
        OnePoleFilter* dampingFilter;
        
        // Mode-specific tap configurations
        static juce::Array<Tap> getTapsForMode(const juce::String& mode);
        
        JUCE_DECLARE_NON_COPYABLE(EarlyReflections)
    };
    
    // ============================================================================
    // Modulation Matrix
    // ============================================================================
    
    /**
     * Modulation matrix for FDN reverb.
     */
    class ModulationMatrix
    {
    public:
        ModulationMatrix(double sampleRate, int numCombs = 4, int numAllpasses = 2);
        ~ModulationMatrix();
        
        void setSampleRate(double sampleRate);
        void setNumFilters(int numCombs, int numAllpasses);
        
        void setRate(float rate);
        void setDepth(float depth);
        
        void setParameters(const juce::NamedValueSet& params);
        
        // Get modulation for a comb filter
        float getCombModulation(int combIndex);
        
        // Get modulation for an allpass filter
        float getAllpassModulation(int allpassIndex);
        
        // Get global modulation
        float getGlobalModulation();
        
        void reset();
        
    private:
        double sampleRate;
        int numCombs;
        int numAllpasses;
        
        juce::OwnedArray<LFO> combLFOs;
        juce::OwnedArray<LFO> allpassLFOs;
        LFO* globalLFO;
        
        juce::Array<float> combModDepths;
        juce::Array<float> allpassModDepths;
        
        float rate;
        float depth;
        
        JUCE_DECLARE_NON_COPYABLE(ModulationMatrix)
    };
    
    // ============================================================================
    // Color System
    // ============================================================================
    
    /**
     * Color system for reverb modes.
     */
    class ColorSystem
    {
    public:
        enum Color { COLOR_1970S, COLOR_1980S, COLOR_NOW };
        
        ColorSystem();
        ~ColorSystem();
        
        void setColor(Color color);
        Color getColor() const;
        
        // Apply color to parameters
        void applyColor(juce::NamedValueSet& params) const;
        
        // Get color name
        juce::String getColorName(Color color) const;
        
        // Get color description
        juce::String getColorDescription(Color color) const;
        
        // List all colors
        juce::Array<Color> listColors() const;
        
    private:
        Color currentColor;
        
        struct ColorParams
        {
            float damping;
            float dampingFreq;
            float diffusion;
            float modRate;
            float modDepth;
            float highCut;
            float bassMult;
        };
        
        juce::Array<ColorParams> colorParams;
        
        JUCE_DECLARE_NON_COPYABLE(ColorSystem)
    };
}
