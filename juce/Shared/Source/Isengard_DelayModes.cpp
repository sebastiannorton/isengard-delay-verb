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
          subtleModulation(nullptr),
          modulationAmount(0.05f)
    {
        subtleModulation = new LFO(0.3f, modulationAmount, sampleRate, LFO::SINE);
    }
    
    HiFiMode::~HiFiMode()
    {
        delete subtleModulation;
    }
    
    float HiFiMode::process(float input)
    {
        // HiFi mode has very subtle modulation
        return DelayModeBase::process(input);
    }
    
    void HiFiMode::processBlock(const float* input, float* output, int numSamples)
    {
        DelayModeBase::processBlock(input, output, numSamples);
    }
    
    void HiFiMode::setSampleRate(double sampleRate)
    {
        DelayModeBase::setSampleRate(sampleRate);
        if (subtleModulation) subtleModulation->setSampleRate(sampleRate);
    }
    
    void HiFiMode::setParameter(const juce::String& paramName, float value)
    {
        DelayModeBase::setParameter(paramName, value);
        if (paramName == "mod_depth") modulationAmount = clamp(value, 0.0f, 0.2f);
    }
    
    void HiFiMode::reset()
    {
        DelayModeBase::reset();
        if (subtleModulation) subtleModulation->reset();
    }
    
    // ============================================================================
    // BBDMode Implementation
    // ============================================================================
    
    BBDMode::BBDMode(double sampleRate)
        : DelayModeBase(sampleRate),
          compander(nullptr),
          clockJitterLFO(nullptr),
          jitterAmount(0.001f),
          noiseTracking(0.05f)
    {
        compander = new OnePoleFilter(1000.0, sampleRate, OnePoleFilter::LOWPASS);
        clockJitterLFO = new LFO(5.0f, jitterAmount, sampleRate, LFO::RANDOM);
    }
    
    BBDMode::~BBDMode()
    {
        delete compander;
        delete clockJitterLFO;
    }
    
    float BBDMode::process(float input)
    {
        // Apply compander (simplified)
        float compressed = compander->process(input);
        
        // Process through base delay
        float delayed = DelayModeBase::process(compressed);
        
        return delayed;
    }
    
    void BBDMode::processBlock(const float* input, float* output, int numSamples)
    {
        DelayModeBase::processBlock(input, output, numSamples);
    }
    
    void BBDMode::setSampleRate(double sampleRate)
    {
        DelayModeBase::setSampleRate(sampleRate);
        if (compander) compander->setSampleRate(sampleRate);
        if (clockJitterLFO) clockJitterLFO->setSampleRate(sampleRate);
    }
    
    void BBDMode::setParameter(const juce::String& paramName, float value)
    {
        DelayModeBase::setParameter(paramName, value);
        if (paramName == "age") jitterAmount = clamp(value, 0.0f, 0.01f);
    }
    
    void BBDMode::reset()
    {
        DelayModeBase::reset();
        if (compander) compander->reset();
        if (clockJitterLFO) clockJitterLFO->reset();
    }
    
    // ============================================================================
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
