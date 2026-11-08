/**
 * Isengard Delay - Audio Plugin Editor Implementation
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#include "PluginProcessor.h"
#include "PluginEditor.h"

// ============================================================================
// Editor Implementation
// ============================================================================

IsengardDelayAudioProcessorEditor::IsengardDelayAudioProcessorEditor(IsengardDelayAudioProcessor& p)
    : AudioProcessorEditor(&p), audioProcessor(p)
{
    // Make sure that before the constructor has finished, you've set the
    // editor's size to whatever you need it to be.
    setSize(800, 600);
    
    // Create UI components
    createControls();
    
    // Set up parameter attachments
    setupParameterAttachments();
}

IsengardDelayAudioProcessorEditor::~IsengardDelayAudioProcessorEditor()
{
}

void IsengardDelayAudioProcessorEditor::createControls()
{
    // Mode selector
    auto* modeLabel = new juce::Label("modeLabel", "Mode:");
    modeLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    modeLabel->setJustificationType(juce::Justification::right);
    modeLabel->setBounds(20, 20, 100, 24);
    addAndMakeVisible(modeLabel);
    labels.add(modeLabel);
    
    auto* modeCombo = new juce::ComboBox("modeCombo");
    modeCombo->setBounds(130, 20, 150, 24);
    modeCombo->addItemList({"Tape", "HiFi", "BBD", "Digital", "Ghost", "Pitch", "RevPitch"}, 1);
    addAndMakeVisible(modeCombo);
    comboBoxes.add(modeCombo);
    
    // Style selector
    auto* styleLabel = new juce::Label("styleLabel", "Style:");
    styleLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    styleLabel->setJustificationType(juce::Justification::right);
    styleLabel->setBounds(20, 50, 100, 24);
    addAndMakeVisible(styleLabel);
    labels.add(styleLabel);
    
    auto* styleCombo = new juce::ComboBox("styleCombo");
    styleCombo->setBounds(130, 50, 150, 24);
    styleCombo->addItemList({"Single", "Dual", "Ratio", "PingPong", "Quad"}, 1);
    addAndMakeVisible(styleCombo);
    comboBoxes.add(styleCombo);
    
    // Mix
    auto* mixLabel = new juce::Label("mixLabel", "Mix:");
    mixLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    mixLabel->setJustificationType(juce::Justification::right);
    mixLabel->setBounds(20, 100, 100, 24);
    addAndMakeVisible(mixLabel);
    labels.add(mixLabel);
    
    auto* mixSlider = new juce::Slider("mixSlider");
    mixSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    mixSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    mixSlider->setBounds(130, 80, 60, 60);
    addAndMakeVisible(mixSlider);
    sliders.add(mixSlider);
    
    // Feedback
    auto* feedbackLabel = new juce::Label("feedbackLabel", "Feedback:");
    feedbackLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    feedbackLabel->setJustificationType(juce::Justification::right);
    feedbackLabel->setBounds(20, 160, 100, 24);
    addAndMakeVisible(feedbackLabel);
    labels.add(feedbackLabel);
    
    auto* feedbackSlider = new juce::Slider("feedbackSlider");
    feedbackSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    feedbackSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    feedbackSlider->setBounds(130, 140, 60, 60);
    addAndMakeVisible(feedbackSlider);
    sliders.add(feedbackSlider);
    
    // Delay Time
    auto* delayLabel = new juce::Label("delayLabel", "Delay Time:");
    delayLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    delayLabel->setJustificationType(juce::Justification::right);
    delayLabel->setBounds(20, 220, 100, 24);
    addAndMakeVisible(delayLabel);
    labels.add(delayLabel);
    
    auto* delaySlider = new juce::Slider("delaySlider");
    delaySlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    delaySlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    delaySlider->setBounds(130, 200, 60, 60);
    addAndMakeVisible(delaySlider);
    sliders.add(delaySlider);
    
    // Mod Rate
    auto* modRateLabel = new juce::Label("modRateLabel", "Mod Rate:");
    modRateLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    modRateLabel->setJustificationType(juce::Justification::right);
    modRateLabel->setBounds(20, 280, 100, 24);
    addAndMakeVisible(modRateLabel);
    labels.add(modRateLabel);
    
    auto* modRateSlider = new juce::Slider("modRateSlider");
    modRateSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    modRateSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    modRateSlider->setBounds(130, 260, 60, 60);
    addAndMakeVisible(modRateSlider);
    sliders.add(modRateSlider);
    
    // Mod Depth
    auto* modDepthLabel = new juce::Label("modDepthLabel", "Mod Depth:");
    modDepthLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    modDepthLabel->setJustificationType(juce::Justification::right);
    modDepthLabel->setBounds(20, 340, 100, 24);
    addAndMakeVisible(modDepthLabel);
    labels.add(modDepthLabel);
    
    auto* modDepthSlider = new juce::Slider("modDepthSlider");
    modDepthSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    modDepthSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    modDepthSlider->setBounds(130, 320, 60, 60);
    addAndMakeVisible(modDepthSlider);
    sliders.add(modDepthSlider);
}

void IsengardDelayAudioProcessorEditor::setupParameterAttachments()
{
    // Clear existing attachments
    sliderAttachments.clear();
    comboAttachments.clear();
    
    // Get APVTS from processor
    auto& apvts = audioProcessor.apvts;
    
    // Find controls by name and attach them
    // Mode combo box
    for (auto* combo : comboBoxes)
    {
        if (combo->getName() == "modeCombo")
        {
            comboAttachments.add(new juce::AudioProcessorValueTreeState::ComboBoxAttachment(
                apvts, "mode", *combo));
        }
        else if (combo->getName() == "styleCombo")
        {
            comboAttachments.add(new juce::AudioProcessorValueTreeState::ComboBoxAttachment(
                apvts, "style", *combo));
        }
    }
    
    // Slider attachments
    for (auto* slider : sliders)
    {
        if (slider->getName() == "mixSlider")
        {
            sliderAttachments.add(new juce::AudioProcessorValueTreeState::SliderAttachment(
                apvts, "mix", *slider));
        }
        else if (slider->getName() == "feedbackSlider")
        {
            sliderAttachments.add(new juce::AudioProcessorValueTreeState::SliderAttachment(
                apvts, "feedback", *slider));
        }
        else if (slider->getName() == "delaySlider")
        {
            sliderAttachments.add(new juce::AudioProcessorValueTreeState::SliderAttachment(
                apvts, "delay_time_ms", *slider));
        }
        else if (slider->getName() == "modRateSlider")
        {
            sliderAttachments.add(new juce::AudioProcessorValueTreeState::SliderAttachment(
                apvts, "mod_rate", *slider));
        }
        else if (slider->getName() == "modDepthSlider")
        {
            sliderAttachments.add(new juce::AudioProcessorValueTreeState::SliderAttachment(
                apvts, "mod_depth", *slider));
        }
    }
}

void IsengardDelayAudioProcessorEditor::paint(juce::Graphics& g)
{
    // Fill background
    g.fillAll(getLookAndFeel().findColour(juce::ResizableWindow::backgroundColourId));
    
    // Draw border
    g.setColour(juce::Colours::darkgrey);
    g.drawRect(0, 0, getWidth(), getHeight(), 1);
    
    // Draw title
    g.setColour(juce::Colours::white);
    g.setFont(juce::Font(24.0f, juce::Font::bold));
    g.drawText("Isengard Delay", getLocalBounds(), juce::Justification::centredTop, true);
    
    // Draw section headers
    g.setFont(juce::Font(16.0f, juce::Font::bold));
    g.setColour(juce::Colours::lightgrey);
    g.drawText("Mode & Style", 20, 80, 200, 24, juce::Justification::left);
    g.drawText("Core Parameters", 20, 140, 200, 24, juce::Justification::left);
    g.drawText("Modulation", 20, 300, 200, 24, juce::Justification::left);
}

void IsengardDelayAudioProcessorEditor::resized()
{
    // In a real implementation, we would update the bounds of all controls
    // when the editor is resized. For now, we'll just keep the fixed layout.
}
