/**
 * Isengard Delay Modes
 * 
 * Base class and implementations for all delay modes.
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#pragma once

#include <JuceHeader.h>
#include "Isengard_DSP.h"

namespace Isengard
{
    /**
     * Base class for all delay modes.
     * 
     * Each mode implements specific DSP characteristics:
     * - Tape: Wow/flutter modulation, tape saturation, mechanical hiss
     * - HiFi: Clean delay with subtle modulation
     * - BBD: BBD compander, clock jitter, noise tracking
     * - Digital: Bit crushing with Age parameter
     * - Ghost: Frequency shifting, ERA-dependent diffusion
     * - Pitch: Pitch shifting in feedback
     * - RevPitch: Reverse delay with pitch shifting
     */
    class DelayModeBase
    {
    public:
        DelayModeBase(double sampleRate);
        virtual ~DelayModeBase();
        
        // Process a single sample
        virtual float process(float input);
        
        // Process a block of samples
        virtual void processBlock(const float* input, float* output, int numSamples);
        
        // Set sample rate
        virtual void setSampleRate(double sampleRate);
        
        // Set a parameter
        virtual void setParameter(const juce::String& paramName, float value);
        
        // Reset the mode processor
        virtual void reset();
        
        // Get the mode name
        virtual juce::String getName() const = 0;
        
    protected:
        double sampleRate;
        
        // Common DSP components used by modes
        DelayLine* delayLine;
        LFO* modulationLFO;
        OnePoleFilter* feedbackFilter;
        
        // Mode-specific parameters
        float feedback;
        float delayTimeMs;
        float modRate;
        float modDepth;
        float age;
        float drive;
        
        // Initialize with default values
        void initializeDefaultParameters();
    };
    
    // ============================================================================
    // Tape Mode
    // ============================================================================
    
    /**
     * Tape delay mode.
     * 
     * Characteristics:
     * - Wow/flutter modulation
     * - Tape saturation
     * - Mechanical hiss
     * - Age-dependent degradation
     */
    class TapeMode : public DelayModeBase
    {
    public:
        TapeMode(double sampleRate);
        ~TapeMode() override;
        
        float process(float input) override;
        void processBlock(const float* input, float* output, int numSamples) override;
        void setSampleRate(double sampleRate) override;
        void setParameter(const juce::String& paramName, float value) override;
        void reset() override;
        
        juce::String getName() const override { return "Tape"; }
        
    private:
        // Tape-specific components
        OnePoleFilter* tapeSaturation;
        OnePoleFilter* hissFilter;
        LFO* wowFlutterLFO;
        
        // Tape parameters
        float wowRate;
        float wowDepth;
        float flutterRate;
        float flutterDepth;
        float saturationAmount;
        float hissAmount;
        
        // Internal state
        float prevInput;
        
        // Apply tape saturation
        float applyTapeSaturation(float x);
        
        // Apply wow/flutter modulation
        float applyWowFlutter(float x);
        
        // Add tape hiss
        float addTapeHiss(float x);
    };
    
    // ============================================================================
    // HiFi Mode
    // ============================================================================
    
    class HiFiMode : public DelayModeBase
    {
    public:
        HiFiMode(double sampleRate);
        ~HiFiMode() override;
        
        float process(float input) override;
        void processBlock(const float* input, float* output, int numSamples) override;
        void setSampleRate(double sampleRate) override;
        void setParameter(const juce::String& paramName, float value) override;
        void reset() override;
        
        juce::String getName() const override { return "HiFi"; }
        
    private:
        LFO* subtleModulation;
        float modulationAmount;
    };
    
    // ============================================================================
    // BBD Mode
    // ============================================================================
    
    class BBDMode : public DelayModeBase
    {
    public:
        BBDMode(double sampleRate);
        ~BBDMode() override;
        
        float process(float input) override;
        void processBlock(const float* input, float* output, int numSamples) override;
        void setSampleRate(double sampleRate) override;
        void setParameter(const juce::String& paramName, float value) override;
        void reset() override;
        
        juce::String getName() const override { return "BBD"; }
        
    private:
        // BBD-specific components
        OnePoleFilter* compander;
        LFO* clockJitterLFO;
        float jitterAmount;
        float noiseTracking;
    };
    
    // ============================================================================
    // Digital Mode
    // ============================================================================
    
    class DigitalMode : public DelayModeBase
    {
    public:
        DigitalMode(double sampleRate);
        ~DigitalMode() override;
        
        float process(float input) override;
        void processBlock(const float* input, float* output, int numSamples) override;
        void setSampleRate(double sampleRate) override;
        void setParameter(const juce::String& paramName, float value) override;
        void reset() override;
        
        juce::String getName() const override { return "Digital"; }
        
    private:
        // Digital-specific: bit crushing
        int bitDepth;
        float bitCrushAmount;
        
        // Apply bit crushing
        float applyBitCrushing(float x);
    };
    
    // ============================================================================
    // Ghost Mode
    // ============================================================================
    
    class GhostMode : public DelayModeBase
    {
    public:
        GhostMode(double sampleRate);
        ~GhostMode() override;
        
        float process(float input) override;
        void processBlock(const float* input, float* output, int numSamples) override;
        void setSampleRate(double sampleRate) override;
        void setParameter(const juce::String& paramName, float value) override;
        void reset() override;
        
        juce::String getName() const override { return "Ghost"; }
        
    private:
        // Ghost-specific: frequency shifting and diffusion
        LFO* frequencyShiftLFO;
        AllpassFilter* diffusionAllpass1;
        AllpassFilter* diffusionAllpass2;
        float frequencyShiftAmount;
        float diffusionAmount;
        float era;
    };
    
    // ============================================================================
    // Pitch Mode
    // ============================================================================
    
    class PitchMode : public DelayModeBase
    {
    public:
        PitchMode(double sampleRate);
        ~PitchMode() override;
        
        float process(float input) override;
        void processBlock(const float* input, float* output, int numSamples) override;
        void setSampleRate(double sampleRate) override;
        void setParameter(const juce::String& paramName, float value) override;
        void reset() override;
        
        juce::String getName() const override { return "Pitch"; }
        
    private:
        // Pitch-specific: pitch shifting in feedback
        float pitchShiftSemitones;
        float pitchDetuneCents;
        
        // Simple pitch shifter (placeholder)
        float applyPitchShift(float x, float semitones);
    };
    
    // ============================================================================
    // RevPitch Mode
    // ============================================================================
    
    class RevPitchMode : public DelayModeBase
    {
    public:
        RevPitchMode(double sampleRate);
        ~RevPitchMode() override;
        
        float process(float input) override;
        void processBlock(const float* input, float* output, int numSamples) override;
        void setSampleRate(double sampleRate) override;
        void setParameter(const juce::String& paramName, float value) override;
        void reset() override;
        
        juce::String getName() const override { return "RevPitch"; }
        
    private:
        // RevPitch-specific: reverse delay with pitch shifting
        DelayLine* reverseBuffer;
        float pitchShiftAmount;
        int reversePosition;
    };
}
