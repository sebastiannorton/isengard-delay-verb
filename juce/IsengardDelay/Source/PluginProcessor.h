/**
 * Isengard Delay - Audio Plugin Processor
 * 
 * This is the main processor for the Isengard Delay AU/VST3 plugin.
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#pragma once

#include <JuceHeader.h>
#include "../Shared/Include/Isengard_DSP.h"
#include "../Shared/Include/Isengard_DelayProcessor.h"

// ============================================================================
// Plugin Parameters
// ============================================================================

namespace IsengardDelay
{
    enum ParameterID
    {
        // Global
        kParamMode = 0,
        kParamStyle,
        kParamMix,
        kParamFeedback,
        
        // Delay
        kParamDelayTimeMs,
        kParamDelayTimeLMs,
        kParamDelayTimeRMs,
        kParamRatio,
        kParamSpread,
        
        // Modulation
        kParamModRate,
        kParamModDepth,
        
        // Character
        kParamAge,
        kParamDrive,
        kParamDiffusion,
        kParamDiffusionSize,
        
        // EQ
        kParamEqHigh,
        kParamEqLow,
        
        // Special
        kParamEra,
        kParamDucking,
        kParamPitchShift,
        kParamPitchDetune,
        kParamFrequencyShift,
        
        kNumParameters
    };
    
    extern const juce::StringArray PARAMETER_IDS;
    extern const juce::StringArray PARAMETER_NAMES;
    extern const juce::Array<juce::NormalisableRange<float>> PARAMETER_RANGES;
}

// ============================================================================
// Plugin Processor
// ============================================================================

class IsengardDelayAudioProcessor : public juce::AudioProcessor
{
public:
    // ============================================================================
    // Constructor/Destructor
    // ============================================================================
    
    IsengardDelayAudioProcessor();
    ~IsengardDelayAudioProcessor() override;
    
    // ============================================================================
    // AudioProcessor Overrides
    // ============================================================================
    
    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;
    void processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages) override;
    
    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override;
    
    const juce::String getName() const override;
    bool acceptsMidi() const override;
    bool producesMidi() const override;
    double getTailLengthSeconds() const override;
    int getNumPrograms() override;
    int getCurrentProgram() override;
    void setCurrentProgram(int index) override;
    const juce::String getProgramName(int index) override;
    void changeProgramName(int index, const juce::String& newName) override;
    
    void getStateInformation(juce::MemoryBlock& destData) override;
    void setStateInformation(const void* data, int sizeInBytes) override;
    
    // ============================================================================
    // Parameter Handling
    // ============================================================================
    
    juce::AudioProcessorValueTreeState apvts;
    
    void setMode(int modeIndex);
    void setStyle(int styleIndex);
    
    // ============================================================================
    // DSP Components
    // ============================================================================
    
private:
    double sampleRate;
    int samplesPerBlock;
    
    // DSP Processor
    Isengard::DelayProcessor* delayProcessor;
    
    // Parameter attachments
    juce::OwnedArray<juce::AudioProcessorValueTreeState::SliderAttachment> parameterAttachments;
    
    // ============================================================================
    // JUCE Required Methods
    // ============================================================================
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(IsengardDelayAudioProcessor)
};

// ============================================================================
// Plugin Editor
// ============================================================================

class IsengardDelayAudioProcessorEditor : public juce::AudioProcessorEditor
{
public:
    IsengardDelayAudioProcessorEditor(IsengardDelayAudioProcessor&);
    ~IsengardDelayAudioProcessorEditor() override;
    
    void paint(juce::Graphics&) override;
    void resized() override;
    
private:
    IsengardDelayAudioProcessor& audioProcessor;
    
    // UI Components
    juce::OwnedArray<juce::Slider> sliders;
    juce::OwnedArray<juce::Label> labels;
    juce::OwnedArray<juce::ComboBox> comboBoxes;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(IsengardDelayAudioProcessorEditor)
};

// ============================================================================
// Plugin Entry Points
// ============================================================================

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter();
