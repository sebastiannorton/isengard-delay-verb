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
#include "Isengard_WowFlutterLFO.h"

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
        OnePoleFilter* tapeSaturationFilter;
        OnePoleFilter* toneFilter;
        OnePoleFilter* dcBlocker;
        WowFlutterLFO* wowFlutterLFO;
        
        // Tape parameters
        float hissAmount;
        float saturationDrive;
        float wowDepth;
        float flutterDepth;
        float tone;
        
        // Apply tape saturation
        float applyTapeSaturation(float x);
        
        // Add tape hiss
        float addTapeHiss(float x);
        
        // Update tone filter based on tone parameter
        void updateToneFilter();
        
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
        LFO* modLFO;
        OnePoleFilter* dcBlocker;
        OnePoleFilter* toneFilter;
        float width;
        float tone;
        
        void updateToneFilter();
    };
    
    // ============================================================================
    // BBD Mode
    // ============================================================================
    
    /**
     * BBD-style compander for noise tracking.
     * 
     * The noise level tracks the signal level, reducing noise when the
     * signal is present and increasing it when the signal is quiet.
     * 
     * Noise Tracking (E017):
     * - noiseScale = max(0.01, 1.0 - signalLevel * 0.9)
     * - noiseLevel = noiseScale * noiseAmount
     */
    class BBDCompander
    {
    public:
        BBDCompander(float noiseAmount = 0.01f, double sampleRate = 44100.0);
        ~BBDCompander();
        
        void setSampleRate(double sampleRate);
        void setNoiseAmount(float amount);
        void setCutoff(float cutoffHz);
        
        float process(float x);
        void reset();
        
    private:
        double sampleRate;
        float noiseAmount;
        OnePoleFilter* lowpass;
        float signalLevel;
        float smoothingAlpha;
        unsigned int noiseSeed;
        
        JUCE_DECLARE_NON_COPYABLE(BBDCompander)
    };
    
    /**
     * Bit depth reduction effect.
     * 
     * Simulates the effect of low bit-depth digital systems by quantizing
     * the signal to a specified number of bits.
     * 
     * Age Mapping (E019):
     * - Age 0% = 24-bit
     * - Age 50% = 12-bit
     * - Age 100% = 8-bit
     * - Formula: bits = 24 - floor(age * 16)
     */
    class BitCrusher
    {
    public:
        BitCrusher(int bits = 16, double sampleRate = 44100.0);
        ~BitCrusher();
        
        void setBits(int bits);
        void setSampleRate(double sampleRate);
        
        float process(float x);
        void reset();
        
    private:
        double sampleRate;
        int bits;
        float step;
        unsigned int ditherSeed;
        
        void updateStep();
        
        JUCE_DECLARE_NON_COPYABLE(BitCrusher)
    };
    
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
        BBDCompander* compander;
        LFO* jitterLFO;
        OnePoleFilter* dcBlocker;
        float noiseAmount;
        float tone;
        
        void updateCompanderCutoff();
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
        BitCrusher* bitCrusher;
        OnePoleFilter* dcBlocker;
        OnePoleFilter* toneFilter;
        float tone;
        
        void updateBitCrusher();
        void updateToneFilter();
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
        float pitchRatio;
        float pitchShiftPhase;
        int pitchShiftBufferPos;
        DelayLine* pitchShiftBuffer;
        
        // Simple pitch shifter
        void updatePitchRatio();
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
        float reverseDelayMs;
        float reversePhase;
    };
}
