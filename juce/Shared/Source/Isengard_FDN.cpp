/**
 * Isengard FDN - Feedback Delay Network Reverb Implementation
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#include "Isengard_FDN.h"

namespace Isengard
{
    // ============================================================================
    // FDNReverb Implementation
    // ============================================================================
    
    FDNReverb::FDNReverb(double sampleRate)
        : sampleRate(sampleRate),
          decay(0.5f),
          size(0.5f),
          damping(0.5f),
          dampingFreq(10000.0f),
          diffusion(0.5f),
          modRate(0.5f),
          modDepth(0.1f),
          preDelayMs(50.0f)
    {
        // Initialize comb filters (4 combs)
        for (int i = 0; i < 4; ++i)
        {
            combFilters.add(new CombFilter(1000.0f + i * 200.0f, 0.8f, sampleRate));
            combDelaysMs.add(1000.0f + i * 200.0f);
            combFeedbacks.add(0.8f);
            dampingFilters.add(new OnePoleFilter(10000.0f, sampleRate, OnePoleFilter::LOWPASS));
        }
        
        // Initialize allpass filters (2 allpasses)
        for (int i = 0; i < 2; ++i)
        {
            allpassFilters.add(new AllpassFilter(5.0f + i * 2.0f, 0.7f, sampleRate));
            allpassDelaysMs.add(5.0f + i * 2.0f);
            allpassFeedbacks.add(0.7f);
        }
        
        // Create feedback matrix
        createOrthogonalMatrix();
        
        // Create diffusion filters
        inputDiffusion = new AllpassFilter(2.0f, 0.5f, sampleRate);
        outputDiffusion = new AllpassFilter(3.0f, 0.5f, sampleRate);
        
        // Create modulation LFOs
        for (int i = 0; i < 4; ++i)
        {
            combLFOs.add(new LFO(modRate * (0.8f + i * 0.1f), modDepth, sampleRate, LFO::SINE));
        }
        for (int i = 0; i < 2; ++i)
        {
            allpassLFOs.add(new LFO(modRate * (1.0f + i * 0.1f), modDepth * 0.8f, sampleRate, LFO::SINE));
        }
        globalLFO = new LFO(modRate, modDepth, sampleRate, LFO::SINE);
        
        combModDepths.addArray({0.1f, 0.1f, 0.1f, 0.1f});
        allpassModDepths.addArray({0.1f, 0.1f});
    }
    
    FDNReverb::~FDNReverb()
    {
        combFilters.clear();
        dampingFilters.clear();
        allpassFilters.clear();
        combLFOs.clear();
        allpassLFOs.clear();
        delete globalLFO;
        delete inputDiffusion;
        delete outputDiffusion;
    }
    
    void FDNReverb::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        for (int i = 0; i < combFilters.size(); ++i)
        {
            combFilters[i]->setSampleRate(sampleRate);
            dampingFilters[i]->setSampleRate(sampleRate);
        }
        for (int i = 0; i < allpassFilters.size(); ++i)
        {
            allpassFilters[i]->setSampleRate(sampleRate);
        }
        for (int i = 0; i < combLFOs.size(); ++i)
        {
            combLFOs[i]->setSampleRate(sampleRate);
        }
        for (int i = 0; i < allpassLFOs.size(); ++i)
        {
            allpassLFOs[i]->setSampleRate(sampleRate);
        }
        globalLFO->setSampleRate(sampleRate);
        inputDiffusion->setSampleRate(sampleRate);
        outputDiffusion->setSampleRate(sampleRate);
    }
    
    void FDNReverb::setDecay(float decay)
    {
        this->decay = clamp(decay, 0.0f, 1.0f);
        updateCombFilters();
    }
    
    void FDNReverb::setSize(float size)
    {
        this->size = clamp(size, 0.0f, 1.0f);
        // Update comb delays based on size
        float baseDelay = 500.0f + 1500.0f * size;
        for (int i = 0; i < combFilters.size(); ++i)
        {
            combDelaysMs.set(i, baseDelay * (0.8f + i * 0.1f));
            combFilters[i]->setDelay(combDelaysMs[i]);
        }
    }
    
    void FDNReverb::setDamping(float damping)
    {
        this->damping = clamp(damping, 0.0f, 1.0f);
        updateDampingFilters();
    }
    
    void FDNReverb::setDampingFreq(float freq)
    {
        this->dampingFreq = clamp(freq, 100.0f, 20000.0f);
        updateDampingFilters();
    }
    
    void FDNReverb::setDiffusion(float diffusion)
    {
        this->diffusion = clamp(diffusion, 0.0f, 1.0f);
        updateAllpassFilters();
    }
    
    void FDNReverb::setModRate(float rate)
    {
        this->modRate = clamp(rate, 0.1f, 10.0f);
        updateModulation();
    }
    
    void FDNReverb::setModDepth(float depth)
    {
        this->modDepth = clamp(depth, 0.0f, 1.0f);
        updateModulation();
    }
    
    void FDNReverb::setPreDelay(float preDelayMs)
    {
        this->preDelayMs = clamp(preDelayMs, 0.0f, 200.0f);
    }
    
    void FDNReverb::setParameters(const juce::NamedValueSet& params)
    {
        if (params.contains("decay")) setDecay(params["decay"]);
        if (params.contains("size")) setSize(params["size"]);
        if (params.contains("damping")) setDamping(params["damping"]);
        if (params.contains("damping_freq")) setDampingFreq(params["damping_freq"]);
        if (params.contains("diffusion")) setDiffusion(params["diffusion"]);
        if (params.contains("mod_rate")) setModRate(params["mod_rate"]);
        if (params.contains("mod_depth")) setModDepth(params["mod_depth"]);
        if (params.contains("pre_delay")) setPreDelay(params["pre_delay"]);
    }
    
    float FDNReverb::processSample(float input)
    {
        // Apply input diffusion
        float x = inputDiffusion->process(input);
        
        // Process through comb filters
        juce::Array<float> combOutputs;
        for (int i = 0; i < combFilters.size(); ++i)
        {
            // Apply modulation to delay time
            float modValue = combLFOs[i]->getValue() * combModDepths[i];
            float originalDelay = combFilters[i]->getDelayTime();
            combFilters[i]->setDelayMs(originalDelay * 1000.0f + modValue * 10.0f);
            
            float combOut = combFilters[i]->process(x);
            
            // Apply damping
            combOut = dampingFilters[i]->process(combOut);
            
            combOutputs.add(combOut);
        }
        
        // Restore original delays
        for (int i = 0; i < combFilters.size(); ++i)
        {
            combFilters[i]->setDelayMs(combDelaysMs[i]);
        }
        
        // Apply feedback matrix
        juce::Array<float> matrixOutputs(combFilters.size(), 0.0f);
        for (int i = 0; i < combFilters.size(); ++i)
        {
            for (int j = 0; j < combFilters.size(); ++j)
            {
                matrixOutputs.set(i, matrixOutputs[i] + feedbackMatrix[i][j] * combOutputs[j]);
            }
        }
        
        // Sum comb outputs
        float combSum = 0.0f;
        for (float val : matrixOutputs)
            combSum += val;
        
        // Process through allpass filters
        float allpassSum = combSum;
        for (int i = 0; i < allpassFilters.size(); ++i)
        {
            allpassSum = allpassFilters[i]->process(allpassSum);
        }
        
        // Apply output diffusion
        return outputDiffusion->process(allpassSum);
    }
    
    void FDNReverb::processBlock(const float* input, float* output, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            output[i] = processSample(input[i]);
        }
    }
    
    void FDNReverb::reset()
    {
        for (int i = 0; i < combFilters.size(); ++i)
        {
            combFilters[i]->reset();
            dampingFilters[i]->reset();
        }
        for (int i = 0; i < allpassFilters.size(); ++i)
        {
            allpassFilters[i]->reset();
        }
        inputDiffusion->reset();
        outputDiffusion->reset();
        for (int i = 0; i < combLFOs.size(); ++i)
        {
            combLFOs[i]->reset();
        }
        for (int i = 0; i < allpassLFOs.size(); ++i)
        {
            allpassLFOs[i]->reset();
        }
        globalLFO->reset();
    }
    
    void FDNReverb::setCombDelays(const float* delaysMs, int numDelays)
    {
        for (int i = 0; i < juce::jmin(numDelays, combFilters.size()); ++i)
        {
            combDelaysMs.set(i, delaysMs[i]);
            combFilters[i]->setDelayMs(delaysMs[i]);
        }
    }
    
    void FDNReverb::setCombFeedbacks(const float* feedbacks, int numFeedbacks)
    {
        for (int i = 0; i < juce::jmin(numFeedbacks, combFilters.size()); ++i)
        {
            combFeedbacks.set(i, feedbacks[i]);
            combFilters[i]->setFeedback(feedbacks[i]);
        }
        updateCombFilters();
    }
    
    void FDNReverb::setAllpassDelays(const float* delaysMs, int numDelays)
    {
        for (int i = 0; i < juce::jmin(numDelays, allpassFilters.size()); ++i)
        {
            allpassDelaysMs.set(i, delaysMs[i]);
            allpassFilters[i]->setDelayMs(delaysMs[i]);
        }
    }
    
    void FDNReverb::setAllpassFeedbacks(const float* feedbacks, int numFeedbacks)
    {
        for (int i = 0; i < juce::jmin(numFeedbacks, allpassFilters.size()); ++i)
        {
            allpassFeedbacks.set(i, feedbacks[i]);
            allpassFilters[i]->setFeedback(feedbacks[i]);
        }
        updateAllpassFilters();
    }
    
    void FDNReverb::createOrthogonalMatrix()
    {
        // Simple orthogonal matrix for 4x4
        for (int i = 0; i < 4; ++i)
        {
            for (int j = 0; j < 4; ++j)
            {
                feedbackMatrix[i][j] = (i == j) ? 0.9f : 0.0f;
            }
        }
        
        // Add some off-diagonal elements for better diffusion
        feedbackMatrix[0][1] = 0.5f;
        feedbackMatrix[1][0] = -0.5f;
        feedbackMatrix[0][2] = 0.3f;
        feedbackMatrix[2][0] = -0.3f;
        feedbackMatrix[1][2] = 0.4f;
        feedbackMatrix[2][1] = -0.4f;
        feedbackMatrix[0][3] = 0.2f;
        feedbackMatrix[3][0] = -0.2f;
        feedbackMatrix[1][3] = 0.3f;
        feedbackMatrix[3][1] = -0.3f;
        feedbackMatrix[2][3] = 0.4f;
        feedbackMatrix[3][2] = -0.4f;
        
        // Normalize to ensure stability
        // (In a real implementation, we'd calculate the spectral radius)
    }
    
    void FDNReverb::updateCombFilters()
    {
        float baseFeedback = 0.9f * decay;
        for (int i = 0; i < combFilters.size(); ++i)
        {
            float feedback = baseFeedback * (0.9f + i * 0.05f);
            combFilters[i]->setFeedback(clamp(feedback, 0.0f, 0.99f));
        }
    }
    
    void FDNReverb::updateAllpassFilters()
    {
        float baseFeedback = 0.5f + 0.4f * diffusion;
        for (int i = 0; i < allpassFilters.size(); ++i)
        {
            allpassFilters[i]->setFeedback(clamp(baseFeedback, 0.0f, 0.99f));
        }
    }
    
    void FDNReverb::updateDampingFilters()
    {
        float cutoff = dampingFreq * (1.0f - damping * 0.8f);
        for (int i = 0; i < dampingFilters.size(); ++i)
        {
            dampingFilters[i]->setCutoff(cutoff);
        }
    }
    
    void FDNReverb::updateModulation()
    {
        for (int i = 0; i < combLFOs.size(); ++i)
        {
            combLFOs[i]->setRate(modRate * (0.8f + i * 0.1f));
            combLFOs[i]->setDepth(modDepth);
        }
        for (int i = 0; i < allpassLFOs.size(); ++i)
        {
            allpassLFOs[i]->setRate(modRate * (1.0f + i * 0.1f));
            allpassLFOs[i]->setDepth(modDepth * 0.8f);
        }
        globalLFO->setRate(modRate);
        globalLFO->setDepth(modDepth);
    }
    
    // ============================================================================
    // EarlyReflections Implementation
    // ============================================================================
    
    EarlyReflections::EarlyReflections(double sampleRate)
        : sampleRate(sampleRate),
          size(0.5f),
          width(0.5f),
          preDelayMs(50.0f),
          earlyLevel(0.5f)
    {
        preDelayLine = new DelayLine(0.2, sampleRate); // 200ms max
        preDelayLine->setDelayMs(preDelayMs);
        
        dampingFilter = new OnePoleFilter(10000.0f, sampleRate, OnePoleFilter::LOWPASS);
        
        // Initialize with default taps
        juce::Array<Tap> defaultTaps;
        defaultTaps.add({20.0f, 0.8f, 0.6f});
        defaultTaps.add({40.0f, 0.6f, 0.8f});
        defaultTaps.add({60.0f, 0.5f, 0.5f});
        defaultTaps.add({80.0f, 0.4f, 0.7f});
        setTaps(defaultTaps);
    }
    
    EarlyReflections::~EarlyReflections()
    {
        delete preDelayLine;
        delete dampingFilter;
        tapDelaysL.clear();
        tapDelaysR.clear();
    }
    
    void EarlyReflections::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        preDelayLine->setSampleRate(sampleRate);
        dampingFilter->setSampleRate(sampleRate);
        for (int i = 0; i < tapDelaysL.size(); ++i)
        {
            tapDelaysL[i]->setSampleRate(sampleRate);
            tapDelaysR[i]->setSampleRate(sampleRate);
        }
    }
    
    void EarlyReflections::setSize(float size)
    {
        this->size = clamp(size, 0.0f, 1.0f);
    }
    
    void EarlyReflections::setWidth(float width)
    {
        this->width = clamp(width, 0.0f, 1.0f);
    }
    
    void EarlyReflections::setPreDelay(float preDelayMs)
    {
        this->preDelayMs = clamp(preDelayMs, 0.0f, 200.0f);
        preDelayLine->setDelayMs(preDelayMs);
    }
    
    void EarlyReflections::setEarlyLevel(float level)
    {
        this->earlyLevel = clamp(level, 0.0f, 1.0f);
    }
    
    void EarlyReflections::setTaps(const juce::Array<Tap>& taps)
    {
        this->taps = taps;
        
        // Recreate tap delays
        tapDelaysL.clear();
        tapDelaysR.clear();
        
        for (const Tap& tap : taps)
        {
            tapDelaysL.add(new DelayLine(tap.delayMs * 0.002, sampleRate));
            tapDelaysR.add(new DelayLine(tap.delayMs * 0.002, sampleRate));
            tapDelaysL.getLast()->setDelayMs(tap.delayMs);
            tapDelaysR.getLast()->setDelayMs(tap.delayMs);
        }
    }
    
    void EarlyReflections::setMode(const juce::String& mode)
    {
        juce::Array<Tap> modeTaps = getTapsForMode(mode);
        setTaps(modeTaps);
    }
    
    void EarlyReflections::processSample(float inputL, float inputR, float* outputL, float* outputR)
    {
        // Apply pre-delay
        float delayedL = preDelayLine->process(inputL);
        float delayedR = preDelayLine->process(inputR);
        
        // Write to all tap delays
        for (int i = 0; i < tapDelaysL.size(); ++i)
        {
            tapDelaysL[i]->process(delayedL);
            tapDelaysR[i]->process(delayedR);
        }
        
        // Process through each tap
        float outL = 0.0f;
        float outR = 0.0f;
        
        for (int i = 0; i < juce::jmin(taps.size(), tapDelaysL.size()); ++i)
        {
            const Tap& tap = taps.getReference(i);
            float tapL = tapDelaysL[i]->read();
            float tapR = tapDelaysR[i]->read();
            
            // Apply gain and stereo panning
            float w = width;
            outL += tapL * tap.gainL * (0.5f + 0.5f * w);
            outR += tapR * tap.gainR * (0.5f + 0.5f * w);
            
            // Cross-feed
            outL += tapR * tap.gainR * (0.5f - 0.5f * w) * 0.5f;
            outR += tapL * tap.gainL * (0.5f - 0.5f * w) * 0.5f;
        }
        
        // Apply damping
        outL = dampingFilter->process(outL);
        outR = dampingFilter->process(outR);
        
        // Apply early level
        *outputL = outL * earlyLevel;
        *outputR = outR * earlyLevel;
    }
    
    void EarlyReflections::processBlock(const float* inputL, const float* inputR,
                                        float* outputL, float* outputR, int numSamples)
    {
        for (int i = 0; i < numSamples; ++i)
        {
            processSample(inputL[i], inputR[i], &outputL[i], &outputR[i]);
        }
    }
    
    void EarlyReflections::reset()
    {
        preDelayLine->reset();
        dampingFilter->reset();
        for (int i = 0; i < tapDelaysL.size(); ++i)
        {
            tapDelaysL[i]->reset();
            tapDelaysR[i]->reset();
        }
    }
    
    juce::Array<EarlyReflections::Tap> EarlyReflections::getTapsForMode(const juce::String& mode)
    {
        juce::Array<Tap> taps;
        
        if (mode == "1972") // EMT 140 Plate
        {
            taps.add({15.0f, 0.6f, 0.5f});
            taps.add({30.0f, 0.4f, 0.6f});
        }
        else if (mode == "1978") // Lexicon 224
        {
            taps.add({25.0f, 0.6f, 0.5f});
            taps.add({50.0f, 0.5f, 0.6f});
            taps.add({75.0f, 0.5f, 0.5f});
            taps.add({100.0f, 0.4f, 0.6f});
        }
        else if (mode == "NOW1") // Modern Algorithm 1
        {
            taps.add({15.0f, 0.55f, 0.35f});
            taps.add({35.0f, 0.5f, 0.4f});
            taps.add({65.0f, 0.45f, 0.45f});
            taps.add({105.0f, 0.4f, 0.5f});
            taps.add({155.0f, 0.35f, 0.55f});
        }
        else // Default
        {
            taps.add({20.0f, 0.8f, 0.6f});
            taps.add({40.0f, 0.6f, 0.8f});
            taps.add({60.0f, 0.5f, 0.5f});
            taps.add({80.0f, 0.4f, 0.7f});
        }
        
        return taps;
    }
    
    // ============================================================================
    // ModulationMatrix Implementation
    // ============================================================================
    
    ModulationMatrix::ModulationMatrix(double sampleRate, int numCombs, int numAllpasses)
        : sampleRate(sampleRate),
          numCombs(numCombs),
          numAllpasses(numAllpasses),
          rate(0.5f),
          depth(0.1f)
    {
        globalLFO = new LFO(rate, depth, sampleRate, LFO::SINE);
        
        for (int i = 0; i < numCombs; ++i)
        {
            combLFOs.add(new LFO(rate * (0.8f + i * 0.1f), depth, sampleRate, LFO::SINE));
            combModDepths.add(0.1f);
        }
        
        for (int i = 0; i < numAllpasses; ++i)
        {
            allpassLFOs.add(new LFO(rate * (1.0f + i * 0.1f), depth * 0.8f, sampleRate, LFO::SINE));
            allpassModDepths.add(0.1f);
        }
    }
    
    ModulationMatrix::~ModulationMatrix()
    {
        delete globalLFO;
        combLFOs.clear();
        allpassLFOs.clear();
    }
    
    void ModulationMatrix::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
        globalLFO->setSampleRate(sampleRate);
        for (int i = 0; i < combLFOs.size(); ++i)
            combLFOs[i]->setSampleRate(sampleRate);
        for (int i = 0; i < allpassLFOs.size(); ++i)
            allpassLFOs[i]->setSampleRate(sampleRate);
    }
    
    void ModulationMatrix::setNumFilters(int numCombs, int numAllpasses)
    {
        this->numCombs = numCombs;
        this->numAllpasses = numAllpasses;
        
        combLFOs.clear();
        allpassLFOs.clear();
        combModDepths.clear();
        allpassModDepths.clear();
        
        for (int i = 0; i < numCombs; ++i)
        {
            combLFOs.add(new LFO(rate * (0.8f + i * 0.1f), depth, sampleRate, LFO::SINE));
            combModDepths.add(0.1f);
        }
        
        for (int i = 0; i < numAllpasses; ++i)
        {
            allpassLFOs.add(new LFO(rate * (1.0f + i * 0.1f), depth * 0.8f, sampleRate, LFO::SINE));
            allpassModDepths.add(0.1f);
        }
    }
    
    void ModulationMatrix::setRate(float rate)
    {
        this->rate = clamp(rate, 0.1f, 10.0f);
        globalLFO->setRate(rate);
        for (int i = 0; i < combLFOs.size(); ++i)
            combLFOs[i]->setRate(rate * (0.8f + i * 0.1f));
        for (int i = 0; i < allpassLFOs.size(); ++i)
            allpassLFOs[i]->setRate(rate * (1.0f + i * 0.1f));
    }
    
    void ModulationMatrix::setDepth(float depth)
    {
        this->depth = clamp(depth, 0.0f, 1.0f);
        globalLFO->setDepth(depth);
        for (int i = 0; i < combLFOs.size(); ++i)
            combLFOs[i]->setDepth(depth);
        for (int i = 0; i < allpassLFOs.size(); ++i)
            allpassLFOs[i]->setDepth(depth * 0.8f);
    }
    
    void ModulationMatrix::setParameters(const juce::NamedValueSet& params)
    {
        if (params.contains("rate")) setRate(params["rate"]);
        if (params.contains("depth")) setDepth(params["depth"]);
    }
    
    float ModulationMatrix::getCombModulation(int combIndex)
    {
        if (combIndex < 0 || combIndex >= combLFOs.size())
            return 0.0f;
        return combLFOs[combIndex]->getValue() * combModDepths[combIndex];
    }
    
    float ModulationMatrix::getAllpassModulation(int allpassIndex)
    {
        if (allpassIndex < 0 || allpassIndex >= allpassLFOs.size())
            return 0.0f;
        return allpassLFOs[allpassIndex]->getValue() * allpassModDepths[allpassIndex];
    }
    
    float ModulationMatrix::getGlobalModulation()
    {
        return globalLFO->getValue();
    }
    
    void ModulationMatrix::reset()
    {
        globalLFO->reset();
        for (int i = 0; i < combLFOs.size(); ++i)
            combLFOs[i]->reset();
        for (int i = 0; i < allpassLFOs.size(); ++i)
            allpassLFOs[i]->reset();
    }
    
    // ============================================================================
    // ColorSystem Implementation
    // ============================================================================
    
    ColorSystem::ColorSystem()
        : currentColor(COLOR_1980S)
    {
        // Initialize color parameters
        ColorParams p1970s = {0.7f, 6000.0f, 0.6f, 0.2f, 0.15f, 8000.0f, 1.2f};
        ColorParams p1980s = {0.5f, 10000.0f, 0.7f, 0.3f, 0.12f, 12000.0f, 1.0f};
        ColorParams pNow = {0.3f, 15000.0f, 0.85f, 0.4f, 0.18f, 18000.0f, 0.9f};
        
        colorParams.add(p1970s);
        colorParams.add(p1980s);
        colorParams.add(pNow);
    }
    
    ColorSystem::~ColorSystem()
    {
    }
    
    void ColorSystem::setColor(Color color)
    {
        currentColor = color;
    }
    
    ColorSystem::Color ColorSystem::getColor() const
    {
        return currentColor;
    }
    
    void ColorSystem::applyColor(juce::NamedValueSet& params) const
    {
        if (currentColor < 0 || currentColor >= colorParams.size())
            return;
        
        const ColorParams& cp = colorParams.getReference(currentColor);
        
        // Apply multiplicative parameters
        if (params.contains("damping"))
            params.set("damping", params["damping"] * cp.damping);
        if (params.contains("diffusion"))
            params.set("diffusion", params["diffusion"] * cp.diffusion);
        if (params.contains("mod_rate"))
            params.set("mod_rate", params["mod_rate"] * cp.modRate);
        if (params.contains("mod_depth"))
            params.set("mod_depth", params["mod_depth"] * cp.modDepth);
        if (params.contains("bass_mult"))
            params.set("bass_mult", params["bass_mult"] * cp.bassMult);
        
        // Apply replacement parameters
        if (params.contains("damping_freq"))
            params.set("damping_freq", cp.dampingFreq);
        if (params.contains("high_cut"))
            params.set("high_cut", cp.highCut);
    }
    
    juce::String ColorSystem::getColorName(Color color) const
    {
        switch (color)
        {
            case COLOR_1970S: return "1970s";
            case COLOR_1980S: return "1980s";
            case COLOR_NOW: return "Now";
            default: return "Unknown";
        }
    }
    
    juce::String ColorSystem::getColorDescription(Color color) const
    {
        switch (color)
        {
            case COLOR_1970S: return "Vintage 1970s - Warmer, darker sound with more damping";
            case COLOR_1980S: return "Classic 1980s - Clean, balanced digital reverb";
            case COLOR_NOW: return "Modern Now - Transparent, dense sound with advanced processing";
            default: return "Unknown color";
        }
    }
    
    juce::Array<ColorSystem::Color> ColorSystem::listColors() const
    {
        juce::Array<Color> colors;
        colors.add(COLOR_1970S);
        colors.add(COLOR_1980S);
        colors.add(COLOR_NOW);
        return colors;
    }
}
