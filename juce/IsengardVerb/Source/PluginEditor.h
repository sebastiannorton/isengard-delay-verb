/**
 * Isengard Verb - Audio Plugin Editor
 * 
 * This is the editor for the Isengard Verb AU/VST3 plugin.
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"

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
    
    // Parameter attachments
    juce::OwnedArray<juce::AudioProcessorValueTreeState::SliderAttachment> sliderAttachments;
    juce::OwnedArray<juce::AudioProcessorValueTreeState::ComboBoxAttachment> comboAttachments;
    
    void createControls();
    void setupParameterAttachments();
    
    // ============================================================================
    // JUCE Required Methods
    // ============================================================================
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(IsengardVerbAudioProcessorEditor)
};
