/**
 * Isengard Delay Modes Implementation
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#include "Isengard_DelayModes.h"
#include "Isengard_DSP.h"
#include "Isengard_WowFlutterLFO.h"
#include <cmath>
#include <cstdlib>
#include <ctime>

namespace Isengard
{
    // ============================================================================
    // DelayModeBase Implementation
    // ============================================================================
    
    DelayModeBase::DelayModeBase(double sampleRate)
        : sampleRate(sampleRate),
          delayLine(nullptr),
          modulationLFO(nullptr),
          feedbackFilter(nullptr),
          feedback(0.5f),
          delayTimeMs(500.0f),
          modRate(0.5f),
          modDepth(0.1f),
          age(0.0f),
          drive(0.0f)
    {
        // Create common DSP components
        delayLine = new DelayLine(5.0, sampleRate); // 5 second max delay
        delayLine->setDelayMs(delayTimeMs);
        
        modulationLFO = new LFO(modRate, modDepth, sampleRate, LFO::SINE);
        feedbackFilter = new OnePoleFilter(1000.0, sampleRate, OnePoleFilter::LOWPASS);
        
        initializeDefaultParameters();
    }
    
    DelayModeBase::~DelayModeBase()
    {
        delete delayLine;
        delete modulationLFO;
        delete feedbackFilter;
    }
    
    float DelayModeBase::process(float input)
    {
        // Basic delay line processing
        float delayed = delayLine->process(input);
        
        // Apply feedback
        float feedbackSignal = delayed * feedback;
        
        // Apply modulation to delay time
        float modValue = modulationLFO->getValue();
        float modDelayTime = delayTimeMs * (1.0f + modDepth * modValue);
        delayLine->setDelayMs(clamp(modDelayTime, 1.0f, 5000.0f));
        
        // Advance LFO
        modulationLFO->processBlock(&modValue, 1);
        
        // Mix dry and wet
        return input + feedbackSignal;
    }
    
    void DelayModeBase::processBlock(const float* input, float* output, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            output[i] = process(input[i]);
        }
    }
    
    void DelayModeBase::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        if (delayLine) delayLine->setSampleRate(sampleRate);
        if (modulationLFO) modulationLFO->setSampleRate(sampleRate);
        if (feedbackFilter) feedbackFilter->setSampleRate(sampleRate);
    }
    
    void DelayModeBase::setParameter(const juce::String& paramName, float value)
    {
        if (paramName == "feedback") feedback = clamp(value, 0.0f, 0.99f);
        else if (paramName == "delay_time_ms") 
        {
            delayTimeMs = clamp(value, 1.0f, 5000.0f);
            if (delayLine) delayLine->setDelayMs(delayTimeMs);
        }
        else if (paramName == "mod_rate") 
        {
            modRate = clamp(value, 0.1f, 10.0f);
            if (modulationLFO) modulationLFO->setRate(modRate);
        }
        else if (paramName == "mod_depth") 
        {
            modDepth = clamp(value, 0.0f, 1.0f);
            if (modulationLFO) modulationLFO->setDepth(modDepth);
        }
        else if (paramName == "age") age = clamp(value, 0.0f, 1.0f);
        else if (paramName == "drive") drive = clamp(value, 0.0f, 1.0f);
    }
    
    void DelayModeBase::reset()
    {
        if (delayLine) delayLine->reset();
        if (modulationLFO) modulationLFO->reset();
        if (feedbackFilter) feedbackFilter->reset();
    }
    
    void DelayModeBase::initializeDefaultParameters()
    {
        feedback = 0.5f;
        delayTimeMs = 500.0f;
        modRate = 0.5f;
        modDepth = 0.1f;
        age = 0.0f;
        drive = 0.0f;
    }
    
    // ============================================================================
    // TapeMode Implementation
    // ============================================================================
    
    TapeMode::TapeMode(double sampleRate)
        : DelayModeBase(sampleRate),
          tapeSaturationFilter(nullptr),
          toneFilter(nullptr),
          dcBlocker(nullptr),
          wowFlutterLFO(nullptr),
          hissAmount(0.001f),
          saturationDrive(0.0f),
          wowDepth(0.3f),
          flutterDepth(0.2f),
          tone(1.0f)
    {
        // Create tape saturation filter (lowpass to smooth saturation)
        tapeSaturationFilter = new OnePoleFilter(5000.0, sampleRate, OnePoleFilter::LOWPASS);
        
        // Create tone filter (lowpass for tape's limited bandwidth)
        toneFilter = new OnePoleFilter(10000.0, sampleRate, OnePoleFilter::LOWPASS);
        
        // Create DC blocker
        dcBlocker = new OnePoleFilter(10.0, sampleRate, OnePoleFilter::HIGHPASS);
        
        // Create wow/flutter LFO
        wowFlutterLFO = new WowFlutterLFO(sampleRate, delayTimeMs);
        wowFlutterLFO->setWowDepth(wowDepth);
        wowFlutterLFO->setFlutterDepth(flutterDepth);
        
        // Seed random for hiss
        std::srand(static_cast<unsigned int>(std::time(nullptr)));
        
        // Update tone filter based on initial tone parameter
        updateToneFilter();
    }
    
    TapeMode::~TapeMode()
    {
        delete tapeSaturationFilter;
        delete toneFilter;
        delete dcBlocker;
        delete wowFlutterLFO;
    }
    
    float TapeMode::process(float input)
    {
        // Step 1: DC blocking
        float blocked = dcBlocker->process(input);
        
        // Step 2: Get modulation values
        auto [wowMod, flutterMod] = wowFlutterLFO->getValues();
        wowFlutterLFO->processSample();
        
        // Step 3: Apply modulation to delay time
        // Calculate modulation amount in samples
        float baseDelaySamples = delayTimeMs / 1000.0f * sampleRate;
        float modAmount = (wowDepth * wowMod + flutterDepth * flutterMod) * modDepth;
        float modSamples = baseDelaySamples * modAmount * 0.005f; // +/- 0.5% max
        
        // Apply modulation to delay line
        delayLine->setDelayMs(delayTimeMs + modSamples * 1000.0f / sampleRate);
        
        // Step 4: Get delayed output (read without writing)
        float delayed = delayLine->read();
        
        // Step 5: Process feedback path
        float feedbackSignal = delayed * feedback;
        
        // Apply tape saturation to feedback
        feedbackSignal = applyTapeSaturation(feedbackSignal);
        
        // Step 6: Mix feedback with input
        float mixed = blocked + feedbackSignal;
        
        // Step 7: Write mixed signal to delay line
        delayLine->process(mixed);
        
        // Step 8: Apply tone filter to delayed output
        float toneFiltered = toneFilter->process(delayed);
        
        // Step 9: Add tape hiss
        float output = addTapeHiss(toneFiltered);
        
        return output;
    }
    
    void TapeMode::processBlock(const float* input, float* output, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            output[i] = process(input[i]);
        }
    }
    
    void TapeMode::setSampleRate(double sampleRate)
    {
        DelayModeBase::setSampleRate(sampleRate);
        if (tapeSaturationFilter) tapeSaturationFilter->setSampleRate(sampleRate);
        if (toneFilter) toneFilter->setSampleRate(sampleRate);
        if (dcBlocker) dcBlocker->setSampleRate(sampleRate);
        if (wowFlutterLFO) wowFlutterLFO->setSampleRate(sampleRate);
    }
    
    void TapeMode::setParameter(const juce::String& paramName, float value)
    {
        DelayModeBase::setParameter(paramName, value);
        
        if (paramName == "drive")
        {
            saturationDrive = clamp(value, 0.0f, 1.0f);
        }
        else if (paramName == "wow_depth")
        {
            wowDepth = clamp(value, 0.0f, 1.0f);
            if (wowFlutterLFO) wowFlutterLFO->setWowDepth(wowDepth);
        }
        else if (paramName == "flutter_depth")
        {
            flutterDepth = clamp(value, 0.0f, 1.0f);
            if (wowFlutterLFO) wowFlutterLFO->setFlutterDepth(flutterDepth);
        }
        else if (paramName == "tone")
        {
            tone = clamp(value, 0.0f, 1.0f);
            updateToneFilter();
        }
        else if (paramName == "hiss")
        {
            hissAmount = clamp(value, 0.0f, 0.005f);
        }
    }
    
    void TapeMode::reset()
    {
        DelayModeBase::reset();
        if (tapeSaturationFilter) tapeSaturationFilter->reset();
        if (toneFilter) toneFilter->reset();
        if (dcBlocker) dcBlocker->reset();
        if (wowFlutterLFO) wowFlutterLFO->reset();
    }
    
    float TapeMode::applyTapeSaturation(float x)
    {
        // Tape saturation using tanh-based soft clipping
        // Input gain: 1.0 + 3.0 * drive
        // Output gain: 1.0 / (1.0 + 0.5 * drive)
        float inputGain = 1.0f + 3.0f * saturationDrive;
        float outputGain = 1.0f / (1.0f + 0.5f * saturationDrive);
        
        // Apply input gain
        x = x * inputGain;
        
        // Soft clipping using tanh
        x = std::tanh(x);
        
        // Apply output gain
        x = x * outputGain;
        
        // Smooth with filter
        if (tapeSaturationFilter)
            x = tapeSaturationFilter->process(x);
        
        return x;
    }
    
    float TapeMode::addTapeHiss(float x)
    {
        // Add subtle hiss noise (tape noise floor)
        if (hissAmount > 0)
        {
            // Generate pseudo-random noise using a simple LCG
            static unsigned int noiseSeed = 12345;
            noiseSeed = noiseSeed * 1103515245 + 12345;
            float random = (noiseSeed >> 16) / 65536.0f * 2.0f - 1.0f;
            x = x + random * hissAmount;
        }
        return x;
    }
    
    void TapeMode::updateToneFilter()
    {
        if (toneFilter)
        {
            // Map tone to cutoff: 0.0 -> 4000Hz, 1.0 -> 15000Hz
            float cutoff = 4000.0f + 11000.0f * tone;
            toneFilter->setCutoff(cutoff);
        }
    }
    
    // ============================================================================
    // HiFiMode Implementation
    // ============================================================================
    
    HiFiMode::HiFiMode(double sampleRate)
        : DelayModeBase(sampleRate),
          modLFO(nullptr),
          dcBlocker(nullptr),
          toneFilter(nullptr),
          width(0.5f),
          tone(0.5f)
    {
        // Create modulation LFO (very subtle, chorus-like)
        modLFO = new LFO(0.5f, 0.001f, sampleRate, LFO::SINE);
        
        // Create DC blocker
        dcBlocker = new OnePoleFilter(10.0, sampleRate, OnePoleFilter::HIGHPASS);
        
        // Create tone filter (highpass for brightness)
        toneFilter = new OnePoleFilter(100.0, sampleRate, OnePoleFilter::HIGHPASS);
        
        // Update tone filter based on initial tone parameter
        updateToneFilter();
    }
    
    HiFiMode::~HiFiMode()
    {
        delete modLFO;
        delete dcBlocker;
        delete toneFilter;
    }
    
    float HiFiMode::process(float input)
    {
        // Step 1: DC blocking
        float blocked = dcBlocker->process(input);
        
        // Step 2: Get modulation value and advance LFO
        float modValue = modLFO->getValue();
        modLFO->processBlock(&modValue, 1);
        
        // Step 3: Apply modulation to delay line
        // HiFi mode has very subtle modulation (0.1% max)
        float baseDelaySamples = delayTimeMs / 1000.0f * sampleRate;
        float modSamples = baseDelaySamples * modDepth * 0.001f; // Scale to 0.1%
        
        delayLine->setDelayMs(delayTimeMs + modSamples * 1000.0f / sampleRate);
        
        // Step 4: Get delayed output (read without writing)
        float delayed = delayLine->read();
        
        // Step 5: Process feedback path
        float feedbackSignal = delayed * feedback;
        
        // Step 6: Mix feedback with input
        float mixed = blocked + feedbackSignal;
        
        // Step 7: Write mixed signal to delay line
        delayLine->process(mixed);
        
        // Step 8: Apply tone filter to delayed output
        float toneFiltered = toneFilter->process(delayed);
        
        return toneFiltered;
    }
    
    void HiFiMode::processBlock(const float* input, float* output, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            output[i] = process(input[i]);
        }
    }
    
    void HiFiMode::setSampleRate(double sampleRate)
    {
        DelayModeBase::setSampleRate(sampleRate);
        if (modLFO) modLFO->setSampleRate(sampleRate);
        if (dcBlocker) dcBlocker->setSampleRate(sampleRate);
        if (toneFilter) toneFilter->setSampleRate(sampleRate);
    }
    
    void HiFiMode::setParameter(const juce::String& paramName, float value)
    {
        DelayModeBase::setParameter(paramName, value);
        
        if (paramName == "mod_rate")
        {
            if (modLFO) modLFO->setRate(clamp(value, 0.1f, 10.0f));
        }
        else if (paramName == "mod_depth")
        {
            // Scale to very small values for HiFi mode (0-0.1%)
            if (modLFO) modLFO->setDepth(clamp(value, 0.0f, 1.0f) * 0.001f);
        }
        else if (paramName == "width")
        {
            width = clamp(value, 0.0f, 1.0f);
        }
        else if (paramName == "tone")
        {
            tone = clamp(value, 0.0f, 1.0f);
            updateToneFilter();
        }
    }
    
    void HiFiMode::reset()
    {
        DelayModeBase::reset();
        if (modLFO) modLFO->reset();
        if (dcBlocker) dcBlocker->reset();
        if (toneFilter) toneFilter->reset();
    }
    
    void HiFiMode::updateToneFilter()
    {
        if (toneFilter)
        {
            // Map tone to cutoff: 0.0 -> 100Hz, 1.0 -> 5000Hz
            float cutoff = 100.0f + 4900.0f * tone;
            toneFilter->setCutoff(cutoff);
        }
    }
    
    // ============================================================================
    // BBDCompander Implementation
    // ============================================================================

    BBDCompander::BBDCompander(float noiseAmount, double sampleRate)
        : sampleRate(sampleRate),
          noiseAmount(clamp(noiseAmount, 0.0f, 0.1f)),
          lowpass(nullptr),
          signalLevel(0.0f),
          smoothingAlpha(0.01f),
          noiseSeed(12345)
    {
        lowpass = new OnePoleFilter(5000.0, sampleRate, OnePoleFilter::LOWPASS);
    }
    
    BBDCompander::~BBDCompander()
    {
        delete lowpass;
    }
    
    void BBDCompander::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        if (lowpass) lowpass->setSampleRate(sampleRate);
    }
    
    void BBDCompander::setNoiseAmount(float amount)
    {
        noiseAmount = clamp(amount, 0.0f, 0.1f);
    }
    
    void BBDCompander::setCutoff(float cutoffHz)
    {
        if (lowpass) lowpass->setCutoff(cutoffHz);
    }
    
    float BBDCompander::process(float x)
    {
        // Update signal level (absolute value for envelope tracking)
        float signalAbs = std::abs(x);
        signalLevel = (1.0f - smoothingAlpha) * signalLevel + smoothingAlpha * signalAbs;
        
        // Calculate noise scale based on signal level (E017)
        // noiseScale = max(0.01, 1.0 - signalLevel * 0.9)
        float noiseScale = std::max(0.01f, 1.0f - signalLevel * 0.9f);
        float noiseLevel = noiseScale * noiseAmount;
        
        // Generate noise using LCG
        noiseSeed = noiseSeed * 1103515245 + 12345;
        float random = (noiseSeed >> 16) / 65536.0f * 2.0f - 1.0f;
        float noise = random * noiseLevel;
        
        // Apply lowpass filter (BBD characteristic)
        float filtered = lowpass->process(x);
        
        // Add noise
        return filtered + noise;
    }
    
    void BBDCompander::reset()
    {
        if (lowpass) lowpass->reset();
        signalLevel = 0.0f;
        noiseSeed = 12345;
    }
    
    // ============================================================================
    // BBDMode Implementation
    // ============================================================================

    BBDMode::BBDMode(double sampleRate)
        : DelayModeBase(sampleRate),
          compander(nullptr),
          jitterLFO(nullptr),
          dcBlocker(nullptr),
          noiseAmount(0.01f),
          tone(0.5f)
    {
        // Create BBD compander
        compander = new BBDCompander(noiseAmount, sampleRate);
        
        // Create clock jitter LFO (random waveform)
        jitterLFO = new LFO(10.0f, 0.001f, sampleRate, LFO::RANDOM);
        
        // Create DC blocker
        dcBlocker = new OnePoleFilter(10.0, sampleRate, OnePoleFilter::HIGHPASS);
        
        // Update compander cutoff based on initial tone
        updateCompanderCutoff();
    }
    
    BBDMode::~BBDMode()
    {
        delete compander;
        delete jitterLFO;
        delete dcBlocker;
    }
    
    float BBDMode::process(float input)
    {
        // Step 1: DC blocking
        float blocked = dcBlocker->process(input);
        
        // Step 2: Apply BBD compander (noise tracking + filtering)
        float companded = compander->process(blocked);
        
        // Step 3: Get jitter modulation value and advance LFO
        float jitterValue = jitterLFO->getValue();
        jitterLFO->processBlock(&jitterValue, 1);
        
        // Step 4: Apply jitter to delay line
        // BBD mode has clock jitter modulation
        float baseDelaySamples = delayTimeMs / 1000.0f * sampleRate;
        float modSamples = baseDelaySamples * modDepth * 0.005f; // Scale to 0.5%
        
        delayLine->setDelayMs(delayTimeMs + modSamples * jitterValue * 1000.0f / sampleRate);
        
        // Step 5: Get delayed output (read without writing)
        float delayed = delayLine->read();
        
        // Step 6: Process feedback path
        float feedbackSignal = delayed * feedback;
        
        // Step 7: Mix feedback with input
        float mixed = companded + feedbackSignal;
        
        // Step 8: Write mixed signal to delay line
        delayLine->process(mixed);
        
        return delayed;
    }
    
    void BBDMode::processBlock(const float* input, float* output, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            output[i] = process(input[i]);
        }
    }
    
    void BBDMode::setSampleRate(double sampleRate)
    {
        DelayModeBase::setSampleRate(sampleRate);
        if (compander) compander->setSampleRate(sampleRate);
        if (jitterLFO) jitterLFO->setSampleRate(sampleRate);
        if (dcBlocker) dcBlocker->setSampleRate(sampleRate);
    }
    
    void BBDMode::setParameter(const juce::String& paramName, float value)
    {
        DelayModeBase::setParameter(paramName, value);
        
        if (paramName == "mod_rate")
        {
            if (jitterLFO) jitterLFO->setRate(clamp(value, 1.0f, 50.0f));
        }
        else if (paramName == "mod_depth")
        {
            // Scale to small values for jitter
            if (jitterLFO) jitterLFO->setDepth(clamp(value, 0.0f, 1.0f) * 0.005f);
        }
        else if (paramName == "noise")
        {
            noiseAmount = clamp(value, 0.0f, 0.1f);
            if (compander) compander->setNoiseAmount(noiseAmount);
        }
        else if (paramName == "tone")
        {
            tone = clamp(value, 0.0f, 1.0f);
            updateCompanderCutoff();
        }
        else if (paramName == "age")
        {
            // Age parameter affects jitter amount
            if (jitterLFO) jitterLFO->setDepth(clamp(value, 0.0f, 1.0f) * 0.01f);
        }
    }
    
    void BBDMode::reset()
    {
        DelayModeBase::reset();
        if (compander) compander->reset();
        if (jitterLFO) jitterLFO->reset();
        if (dcBlocker) dcBlocker->reset();
    }
    
    void BBDMode::updateCompanderCutoff()
    {
        if (compander)
        {
            // Map tone to BBD lowpass cutoff: 0.0 -> 2000Hz, 1.0 -> 8000Hz
            float cutoff = 2000.0f + 6000.0f * tone;
            compander->setCutoff(cutoff);
        }
    }
    // DigitalMode Implementation
    // ============================================================================
    
    DigitalMode::DigitalMode(double sampleRate)
        : DelayModeBase(sampleRate),
          bitDepth(16),
          bitCrushAmount(0.0f)
    {
    }
    
    DigitalMode::~DigitalMode()
    {
    }
    
    float DigitalMode::process(float input)
    {
        // Apply bit crushing
        float crushed = applyBitCrushing(input);
        
        // Process through base delay
        float delayed = DelayModeBase::process(crushed);
        
        return delayed;
    }
    
    void DigitalMode::processBlock(const float* input, float* output, int numSamples)
    {
        DelayModeBase::processBlock(input, output, numSamples);
    }
    
    void DigitalMode::setSampleRate(double sampleRate)
    {
        DelayModeBase::setSampleRate(sampleRate);
    }
    
    void DigitalMode::setParameter(const juce::String& paramName, float value)
    {
        DelayModeBase::setParameter(paramName, value);
        if (paramName == "age") bitCrushAmount = clamp(value, 0.0f, 1.0f);
    }
    
    void DigitalMode::reset()
    {
        DelayModeBase::reset();
    }
    
    float DigitalMode::applyBitCrushing(float x)
    {
        if (bitCrushAmount > 0)
        {
            // Reduce bit depth based on age parameter
            int reducedBits = juce::jlimit(1, 24, static_cast<int>(16 * (1.0f - bitCrushAmount)));
            float scale = static_cast<float>((1 << reducedBits) - 1);
            x = std::round(x * scale) / scale;
        }
        return x;
    }
    
    // ============================================================================
    // GhostMode Implementation (Placeholder)
    // ============================================================================
    
    GhostMode::GhostMode(double sampleRate)
        : DelayModeBase(sampleRate),
          frequencyShiftLFO(nullptr),
          diffusionAllpass1(nullptr),
          diffusionAllpass2(nullptr),
          frequencyShiftAmount(0.0f),
          diffusionAmount(0.5f),
          era(0.5f)
    {
        frequencyShiftLFO = new LFO(0.5f, 0.0f, sampleRate, LFO::SINE);
        diffusionAllpass1 = new AllpassFilter(100.0, 0.5f, sampleRate);
        diffusionAllpass2 = new AllpassFilter(150.0, 0.5f, sampleRate);
    }
    
    GhostMode::~GhostMode()
    {
        delete frequencyShiftLFO;
        delete diffusionAllpass1;
        delete diffusionAllpass2;
    }
    
    float GhostMode::process(float input)
    {
        return DelayModeBase::process(input);
    }
    
    void GhostMode::processBlock(const float* input, float* output, int numSamples)
    {
        DelayModeBase::processBlock(input, output, numSamples);
    }
    
    void GhostMode::setSampleRate(double sampleRate)
    {
        DelayModeBase::setSampleRate(sampleRate);
        if (frequencyShiftLFO) frequencyShiftLFO->setSampleRate(sampleRate);
        if (diffusionAllpass1) diffusionAllpass1->setSampleRate(sampleRate);
        if (diffusionAllpass2) diffusionAllpass2->setSampleRate(sampleRate);
    }
    
    void GhostMode::setParameter(const juce::String& paramName, float value)
    {
        DelayModeBase::setParameter(paramName, value);
        if (paramName == "frequency_shift") frequencyShiftAmount = value;
        else if (paramName == "diffusion") diffusionAmount = value;
        else if (paramName == "era") era = value;
    }
    
    void GhostMode::reset()
    {
        DelayModeBase::reset();
        if (frequencyShiftLFO) frequencyShiftLFO->reset();
        if (diffusionAllpass1) diffusionAllpass1->reset();
        if (diffusionAllpass2) diffusionAllpass2->reset();
    }
    
    // ============================================================================
    // PitchMode Implementation (Placeholder)
    // ============================================================================
    
    PitchMode::PitchMode(double sampleRate)
        : DelayModeBase(sampleRate),
          pitchShiftSemitones(0.0f),
          pitchDetuneCents(0.0f)
    {
    }
    
    PitchMode::~PitchMode()
    {
    }
    
    float PitchMode::process(float input)
    {
        return DelayModeBase::process(input);
    }
    
    void PitchMode::processBlock(const float* input, float* output, int numSamples)
    {
        DelayModeBase::processBlock(input, output, numSamples);
    }
    
    void PitchMode::setSampleRate(double sampleRate)
    {
        DelayModeBase::setSampleRate(sampleRate);
    }
    
    void PitchMode::setParameter(const juce::String& paramName, float value)
    {
        DelayModeBase::setParameter(paramName, value);
        if (paramName == "pitch_shift") pitchShiftSemitones = value;
        else if (paramName == "pitch_detune") pitchDetuneCents = value;
    }
    
    void PitchMode::reset()
    {
        DelayModeBase::reset();
    }
    
    float PitchMode::applyPitchShift(float x, float semitones)
    {
        // Placeholder - actual pitch shifting would be more complex
        return x;
    }
    
    // ============================================================================
    // RevPitchMode Implementation (Placeholder)
    // ============================================================================
    
    RevPitchMode::RevPitchMode(double sampleRate)
        : DelayModeBase(sampleRate),
          reverseBuffer(nullptr),
          pitchShiftAmount(0.0f),
          reversePosition(0)
    {
        reverseBuffer = new DelayLine(5.0, sampleRate);
    }
    
    RevPitchMode::~RevPitchMode()
    {
        delete reverseBuffer;
    }
    
    float RevPitchMode::process(float input)
    {
        return DelayModeBase::process(input);
    }
    
    void RevPitchMode::processBlock(const float* input, float* output, int numSamples)
    {
        DelayModeBase::processBlock(input, output, numSamples);
    }
    
    void RevPitchMode::setSampleRate(double sampleRate)
    {
        DelayModeBase::setSampleRate(sampleRate);
        if (reverseBuffer) reverseBuffer->setSampleRate(sampleRate);
    }
    
    void RevPitchMode::setParameter(const juce::String& paramName, float value)
    {
        DelayModeBase::setParameter(paramName, value);
        if (paramName == "pitch_shift") pitchShiftAmount = value;
    }
    
    void RevPitchMode::reset()
    {
        DelayModeBase::reset();
        if (reverseBuffer) reverseBuffer->reset();
        reversePosition = 0;
    }
}
