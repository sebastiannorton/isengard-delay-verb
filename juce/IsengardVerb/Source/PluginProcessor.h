/**
 * Isengard Verb - Audio Plugin Processor
 * 
 * This is the main processor for the Isengard Verb AU/VST3 plugin.
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#pragma once

#include <JuceHeader.h>
#include "../../Shared/Include/Isengard_FDN.h"
#include "../../Shared/Include/Isengard_VerbProcessor.h"

// ============================================================================
// Plugin Parameters
// ============================================================================

namespace IsengardVerb
{
    enum ParameterID
    {
        // Global
        kParamMode = 0,
        kParamColor,
        kParamMix,
        
        // Reverb Core
        kParamDecay,
        kParamSize,
        kParamPreDelay,
        kParamAttack,
        
        // Frequency Controls
        kParamBassMult,
        kParamBassXover,
        kParamHighCut,
        kParamDamping,
        kParamDampingFreq,
        
        // Modulation
        kParamModRate,
        kParamModDepth,
        
        // Stereo
        kParamWidth,
        kParamEarlyLateBalance,
        
        kNumParameters
    };
    
    extern const juce::StringArray PARAMETER_IDS;
    extern const juce::StringArray PARAMETER_NAMES;
    extern const juce::Array<juce::NormalisableRange<float>> PARAMETER_RANGES;
    
    // Mode names (22 modes)
    extern const juce::StringArray MODE_NAMES;
    
    // Color names (3 colors)
    extern const juce::StringArray COLOR_NAMES;
}

// ============================================================================
// Plugin Processor
// ============================================================================

class IsengardVerbAudioProcessor : public juce::AudioProcessor
{
public:
    // ============================================================================
    // Constructor/Destructor
    // ============================================================================
    
    IsengardVerbAudioProcessor();
    ~IsengardVerbAudioProcessor() override;
    
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
    void setColor(int colorIndex);
    
    // ============================================================================
    // DSP Components
    // ============================================================================
    
private:
    double sampleRate;
    int samplesPerBlock;
    
    // DSP Processor
    Isengard::VerbProcessor* verbProcessor;
    
    // Parameter attachments
    juce::OwnedArray<juce::AudioProcessorValueTreeState::SliderAttachment> parameterAttachments;
    juce::OwnedArray<juce::AudioProcessorValueTreeState::ComboBoxAttachment> comboBoxAttachments;
    
    juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout();
    void updateParameters();
    
    // ============================================================================
    // JUCE Required Methods
    // ============================================================================
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(IsengardVerbAudioProcessor)
};

// ============================================================================
// Plugin Editor
// ============================================================================

class IsengardVerbAudioProcessorEditor : public juce::AudioProcessorEditor
{
public:
    IsengardVerbAudioProcessorEditor(IsengardVerbAudioProcessor&);
    ~IsengardVerbAudioProcessorEditor() override;
    
    void paint(juce::Graphics&) override;
    void resized() override;
    
private:
    IsengardVerbAudioProcessor& audioProcessor;
    
    // UI Components
    juce::OwnedArray<juce::Slider> sliders;
    juce::OwnedArray<juce::Label> labels;
    juce::OwnedArray<juce::ComboBox> comboBoxes;
    
    void createControls();
    void setupParameterAttachments();
    
    // ============================================================================
    // JUCE Required Methods
    // ============================================================================
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(IsengardVerbAudioProcessorEditor)
};

// ============================================================================
// Plugin Entry Points
// ============================================================================

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter();
