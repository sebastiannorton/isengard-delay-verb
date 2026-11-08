/**
 * Isengard Delay Styles
 * 
 * Base class and implementations for all delay styles.
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#pragma once

#include <JuceHeader.h>
#include "Isengard_DSP.h"

namespace Isengard
{
    // Forward declaration
    class DelayModeBase;
    
    /**
     * Base class for all delay styles.
     * 
     * Styles determine how delay signals are routed in stereo:
     * - Single: Mono delay
     * - Dual: Two independent delays (L/R)
     * - Ratio: Delay times related by ratio
     * - PingPong: Delay bounces between channels
     * - Quad: Four-tap delay with stereo spread
     */
    class DelayStyleBase
    {
    public:
        DelayStyleBase(double sampleRate);
        virtual ~DelayStyleBase();
        
        // Process a single sample (mono)
        virtual float process(float input);
        
        // Process stereo samples
        virtual std::pair<float, float> process(float leftInput, float rightInput);
        
        // Process a block of samples
        virtual void processBlock(const float* inputL, const float* inputR, float* outputL, float* outputR, int numSamples);
        
        // Set sample rate
        virtual void setSampleRate(double sampleRate);
        
        // Set a parameter
        virtual void setParameter(const juce::String& paramName, float value);
        
        // Set the mode processor (for styles that need to interact with mode)
        virtual void setModeProcessor(DelayModeBase* mode);
        
        // Reset the style processor
        virtual void reset();
        
        // Get the style name
        virtual juce::String getName() const = 0;
        
    protected:
        double sampleRate;
        DelayModeBase* modeProcessor;
        
        // Style-specific parameters
        float spread;
        float ratio;
        
        // Delay lines for stereo processing
        DelayLine* delayLineL;
        DelayLine* delayLineR;
        
        void initializeDefaultParameters();
    };
    
    // ============================================================================
    // Single Style
    // ============================================================================
    
    /**
     * Single delay style.
     * 
     * Mono delay - both channels get the same delayed signal.
     */
    class SingleStyle : public DelayStyleBase
    {
    public:
        SingleStyle(double sampleRate);
        ~SingleStyle() override;
        
        float process(float input) override;
        std::pair<float, float> process(float leftInput, float rightInput) override;
        void processBlock(const float* inputL, const float* inputR, float* outputL, float* outputR, int numSamples) override;
        void setSampleRate(double sampleRate) override;
        void setParameter(const juce::String& paramName, float value) override;
        void setModeProcessor(DelayModeBase* mode) override;
        void reset() override;
        
        juce::String getName() const override { return "Single"; }
    };
    
    // ============================================================================
    // Dual Style
    // ============================================================================
    
    /**
     * Dual delay style.
     * 
     * Two independent delays for left and right channels.
     */
    class DualStyle : public DelayStyleBase
    {
    public:
        DualStyle(double sampleRate);
        ~DualStyle() override;
        
        float process(float input) override;
        std::pair<float, float> process(float leftInput, float rightInput) override;
        void processBlock(const float* inputL, const float* inputR, float* outputL, float* outputR, int numSamples) override;
        void setSampleRate(double sampleRate) override;
        void setParameter(const juce::String& paramName, float value) override;
        void setModeProcessor(DelayModeBase* mode) override;
        void reset() override;
        
        juce::String getName() const override { return "Dual"; }
        
    private:
        float delayTimeLMs;
        float delayTimeRMs;
    };
    
    // ============================================================================
    // Ratio Style
    // ============================================================================
    
    /**
     * Ratio delay style.
     * 
     * Right channel delay is a ratio of the left channel delay.
     */
    class RatioStyle : public DelayStyleBase
    {
    public:
        RatioStyle(double sampleRate);
        ~RatioStyle() override;
        
        float process(float input) override;
        std::pair<float, float> process(float leftInput, float rightInput) override;
        void processBlock(const float* inputL, const float* inputR, float* outputL, float* outputR, int numSamples) override;
        void setSampleRate(double sampleRate) override;
        void setParameter(const juce::String& paramName, float value) override;
        void setModeProcessor(DelayModeBase* mode) override;
        void reset() override;
        
        juce::String getName() const override { return "Ratio"; }
    };
    
    // ============================================================================
    // PingPong Style
    // ============================================================================
    
    /**
     * PingPong delay style.
     * 
     * Delay bounces between left and right channels.
     */
    class PingPongStyle : public DelayStyleBase
    {
    public:
        PingPongStyle(double sampleRate);
        ~PingPongStyle() override;
        
        float process(float input) override;
        std::pair<float, float> process(float leftInput, float rightInput) override;
        void processBlock(const float* inputL, const float* inputR, float* outputL, float* outputR, int numSamples) override;
        void setSampleRate(double sampleRate) override;
        void setParameter(const juce::String& paramName, float value) override;
        void setModeProcessor(DelayModeBase* mode) override;
        void reset() override;
        
        juce::String getName() const override { return "PingPong"; }
        
    private:
        bool pingPongDirection; // true = L->R, false = R->L
    };
    
    // ============================================================================
    // Quad Style
    // ============================================================================
    
    /**
     * Quad delay style.
     * 
     * Four-tap delay with stereo spread.
     */
    class QuadStyle : public DelayStyleBase
    {
    public:
        QuadStyle(double sampleRate);
        ~QuadStyle() override;
        
        float process(float input) override;
        std::pair<float, float> process(float leftInput, float rightInput) override;
        void processBlock(const float* inputL, const float* inputR, float* outputL, float* outputR, int numSamples) override;
        void setSampleRate(double sampleRate) override;
        void setParameter(const juce::String& paramName, float value) override;
        void setModeProcessor(DelayModeBase* mode) override;
        void reset() override;
        
        juce::String getName() const override { return "Quad"; }
        
    private:
        DelayLine* delayLineL1;
        DelayLine* delayLineL2;
        DelayLine* delayLineR1;
        DelayLine* delayLineR2;
    };
}
