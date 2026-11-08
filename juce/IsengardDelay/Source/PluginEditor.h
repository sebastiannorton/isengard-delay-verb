/**
 * Isengard Delay - Audio Plugin Editor
 * 
 * This is the editor for the Isengard Delay AU/VST3 plugin.
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"

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
    
    void createControls();
    void setupParameterAttachments();
    
    // ============================================================================
    // JUCE Required Methods
    // ============================================================================
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(IsengardDelayAudioProcessorEditor)
};
