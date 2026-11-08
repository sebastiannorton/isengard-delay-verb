/**
 * Isengard DSP - Shared DSP Components
 * 
 * This header provides the shared DSP components for Isengard Delay and Verb plugins.
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#pragma once

#include <JuceHeader.h>

// ============================================================================
// Constants
// ============================================================================

namespace Isengard
{
    const double DEFAULT_SAMPLE_RATE = 44100.0;
    const int MAX_BLOCK_SIZE = 2048;
    const int MAX_CHANNELS = 2;
    const double PI = juce::MathConstants<double>::pi;
    const double TWO_PI = juce::MathConstants<double>::twoPi;
}

// ============================================================================
// Utility Functions
// ============================================================================

namespace Isengard
{
    /** Clamp a value between min and max */
    template <typename T>
    T clamp(T value, T minVal, T maxVal) {
        return juce::jlimit(minVal, maxVal, value);
    }
    
    /** Linear interpolation */
    template <typename T>
    T lerp(T a, T b, T t) {
        return a + (b - a) * t;
    }
    
    /** Convert milliseconds to samples */
    int msToSamples(double ms, double sampleRate);
    
    /** Convert samples to milliseconds */
    double samplesToMs(int samples, double sampleRate);
    
    /** Cubic interpolation */
    float cubicInterpolate(const float* data, float fractionalIndex, int bufferSize);
    
    /** Denormal number prevention */
    float denormalPrevent(float x);
}

// ============================================================================
// Delay Line
// ============================================================================

namespace Isengard
{
    /**
     * Circular buffer delay line with cubic interpolation.
     * 
     * Features:
     * - Circular buffer with efficient wrap-around
     * - Cubic interpolation for fractional delays
     * - Sample rate independent
     * - No dynamic allocation during processing
     */
    class DelayLine
    {
    public:
        DelayLine(double maxDelaySeconds, double sampleRate);
        ~DelayLine();
        
        // Set sample rate
        void setSampleRate(double sampleRate);
        
        // Set delay time in seconds
        void setDelayTime(double delaySeconds);
        
        // Set delay time in milliseconds
        void setDelayMs(double delayMs);
        
        // Process a single sample (write and read)
        float process(float input);
        
        // Read the current delayed output without writing
        float read() const;
        
        // Process a block of samples
        void processBlock(const float* input, float* output, int numSamples);
        
        // Reset the delay line
        void reset();
        
        // Get current delay time in seconds
        double getDelayTime() const { return delaySeconds; }
        
    private:
        double sampleRate;
        double maxDelaySeconds;
        int bufferSize;
        int writePos;
        double delaySeconds;
        double delaySamples;
        juce::HeapBlock<float> buffer;
        
        // For cubic interpolation
        mutable int prevReadPos[4];
        mutable float prevSamples[4];
        
        int calculateReadPosition() const;
        float readWithInterpolation(int readPos) const;
        
        JUCE_DECLARE_NON_COPYABLE(DelayLine)
    };
}

// ============================================================================
// One Pole Filter
// ============================================================================

namespace Isengard
{
    /**
     * One-pole filter (lowpass or highpass).
     * 
     * Implementation: y[n] = a * x[n] + (1 - a) * y[n-1]
     * For lowpass: a = 1 - exp(-2 * pi * fc / sr)
     * For highpass: a = exp(-2 * pi * fc / sr)
     */
    class OnePoleFilter
    {
    public:
        enum FilterType { LOWPASS, HIGHPASS };
        
        OnePoleFilter(double cutoffHz, double sampleRate, FilterType type = LOWPASS);
        ~OnePoleFilter();
        
        void setSampleRate(double sampleRate);
        void setCutoff(double cutoffHz);
        void setType(FilterType type);
        
        float process(float input);
        void processBlock(const float* input, float* output, int numSamples);
        void reset();
        
    private:
        double sampleRate;
        double cutoffHz;
        FilterType type;
        double a;
        float y1;
        
        void updateCoefficients();
        
        JUCE_DECLARE_NON_COPYABLE(OnePoleFilter)
    };
}

// ============================================================================
// Biquad Filter
// ============================================================================

namespace Isengard
{
    /**
     * Biquad filter supporting multiple types.
     */
    class BiquadFilter
    {
    public:
        enum FilterType { LOWPASS, HIGHPASS, BANDPASS, NOTCH, PEAK, LOWSHELF, HIGHSHELF };
        
        BiquadFilter(double freq, double Q, double gainDB, double sampleRate, FilterType type = LOWPASS);
        ~BiquadFilter();
        
        void setSampleRate(double sampleRate);
        void setParameters(double freq, double Q, double gainDB);
        void setType(FilterType type);
        
        float process(float input);
        void processBlock(const float* input, float* output, int numSamples);
        void reset();
        
    private:
        double sampleRate;
        double freq;
        double Q;
        double gainDB;
        FilterType type;
        
        // Filter coefficients
        double a0, a1, a2, b1, b2;
        
        // State
        float x1, x2, y1, y2;
        
        void updateCoefficients();
        
        JUCE_DECLARE_NON_COPYABLE(BiquadFilter)
    };
}

// ============================================================================
// Comb Filter
// ============================================================================

namespace Isengard
{
    /**
     * Comb filter for FDN reverb.
     * 
     * Implementation: y[n] = x[n] + feedback * y[n - delay]
     */
    class CombFilter
    {
    public:
        CombFilter(double delayMs, float feedback, double sampleRate);
        ~CombFilter();
        
        void setSampleRate(double sampleRate);
        void setDelay(double delayMs);
        void setFeedback(float feedback);
        
        float process(float input);
        void reset();
        
    private:
        DelayLine* delayLine;
        float feedback;
        
        JUCE_DECLARE_NON_COPYABLE(CombFilter)
    };
}

// ============================================================================
// Allpass Filter
// ============================================================================

namespace Isengard
{
    /**
     * Allpass filter for diffusion.
     * 
     * Implementation: y[n] = -x[n] + feedback * y[n - delay] + x[n - delay]
     */
    class AllpassFilter
    {
    public:
        AllpassFilter(double delayMs, float feedback, double sampleRate);
        ~AllpassFilter();
        
        void setSampleRate(double sampleRate);
        void setDelay(double delayMs);
        void setFeedback(float feedback);
        
        float process(float input);
        void reset();
        
    private:
        DelayLine* delayLine;
        float feedback;
        
        JUCE_DECLARE_NON_COPYABLE(AllpassFilter)
    };
}

// ============================================================================
// LFO (Low Frequency Oscillator)
// ============================================================================

namespace Isengard
{
    /**
     * Low Frequency Oscillator for modulation.
     */
    class LFO
    {
    public:
        enum Waveform { SINE, TRIANGLE, SQUARE, RANDOM };
        
        LFO(double rate, double depth, double sampleRate, Waveform waveform = SINE);
        ~LFO();
        
        void setSampleRate(double sampleRate);
        void setRate(double rate);
        void setDepth(double depth);
        void setWaveform(Waveform waveform);
        void setOffset(double offset);
        
        float getValue();
        void processBlock(float* output, int numSamples);
        void reset();
        
    private:
        double sampleRate;
        double rate;
        double depth;
        double offset;
        Waveform waveform;
        double phase;
        
        // For random waveform
        double randomPhase;
        double randomRate;
        float randomValue;
        juce::Random rng;
        
        JUCE_DECLARE_NON_COPYABLE(LFO)
    };
}

// ============================================================================
// Smoothed Parameter
// ============================================================================

namespace Isengard
{
    /**
     * Smoothed parameter for click-free automation.
     * Uses exponential smoothing: y[n] = alpha * target + (1 - alpha) * y[n-1]
     */
    class SmoothedParameter
    {
    public:
        SmoothedParameter(float initialValue, float minValue, float maxValue, 
                         double smoothingTimeMs, double sampleRate);
        ~SmoothedParameter();
        
        void setSampleRate(double sampleRate);
        void setSmoothingTime(double smoothingTimeMs);
        void setRange(float minValue, float maxValue);
        
        void setTarget(float value);
        float getValue() const;
        float getTarget() const;
        
        void processSample();
        void processBlock(int numSamples);
        void reset();
        
    private:
        float minValue;
        float maxValue;
        double smoothingTimeMs;
        double sampleRate;
        float targetValue;
        float currentValue;
        double alpha;
        
        void updateAlpha();
        
        JUCE_DECLARE_NON_COPYABLE(SmoothedParameter)
    };
}

// ============================================================================
// Parameter System
// ============================================================================

namespace Isengard
{
    /**
     * Parameter system with double buffering for thread safety.
     */
    class ParameterSystem
    {
    public:
        ParameterSystem(double sampleRate);
        ~ParameterSystem();
        
        void setSampleRate(double sampleRate);
        
        // Add a parameter
        void addParameter(const juce::String& id, float initialValue, 
                         float minValue, float maxValue, double smoothingTimeMs = 0.0,
                         bool logarithmic = false);
        
        // Set parameter value (non-audio thread)
        void setParameter(const juce::String& id, float value);
        
        // Get parameter value (audio thread)
        float getParameter(const juce::String& id) const;
        
        // Get smoothed parameter value
        float getSmoothedParameter(const juce::String& id);
        
        // Process block (audio thread)
        void processBlock(int numSamples);
        
        // Reset all parameters
        void reset();
        
        // Get all parameter IDs
        juce::StringArray getParameterIDs() const;
        
    private:
        double sampleRate;
        juce::OwnedArray<SmoothedParameter> parameters;
        juce::StringArray parameterIDs;
        juce::CriticalSection lock;
        
        JUCE_DECLARE_NON_COPYABLE(ParameterSystem)
    };
}
