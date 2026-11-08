/**
 * Isengard Verb - Audio Plugin Editor Implementation
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#include "PluginProcessor.h"
#include "PluginEditor.h"

// ============================================================================
// Editor Implementation
// ============================================================================

IsengardVerbAudioProcessorEditor::IsengardVerbAudioProcessorEditor(IsengardVerbAudioProcessor& p)
    : AudioProcessorEditor(&p), audioProcessor(p)
{
    // Make sure that before the constructor has finished, you've set the
    // editor's size to whatever you need it to be.
    setSize(900, 700);
    
    // Create UI components
    createControls();
    
    // Set up parameter attachments
    setupParameterAttachments();
}

IsengardVerbAudioProcessorEditor::~IsengardVerbAudioProcessorEditor()
{
}

void IsengardVerbAudioProcessorEditor::createControls()
{
    // Row 1: Mode and Color selectors
    
    // Mode selector
    auto* modeLabel = new juce::Label("modeLabel", "Mode:");
    modeLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    modeLabel->setJustificationType(juce::Justification::right);
    modeLabel->setBounds(20, 20, 100, 24);
    addAndMakeVisible(modeLabel);
    labels.add(modeLabel);
    
    auto* modeCombo = new juce::ComboBox("modeCombo");
    modeCombo->setBounds(130, 20, 180, 24);
    modeCombo->addItemList(IsengardVerb::MODE_NAMES, 1);
    addAndMakeVisible(modeCombo);
    comboBoxes.add(modeCombo);
    
    // Color selector
    auto* colorLabel = new juce::Label("colorLabel", "Color:");
    colorLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    colorLabel->setJustificationType(juce::Justification::right);
    colorLabel->setBounds(320, 20, 100, 24);
    addAndMakeVisible(colorLabel);
    labels.add(colorLabel);
    
    auto* colorCombo = new juce::ComboBox("colorCombo");
    colorCombo->setBounds(430, 20, 120, 24);
    colorCombo->addItemList(IsengardVerb::COLOR_NAMES, 1);
    addAndMakeVisible(colorCombo);
    comboBoxes.add(colorCombo);
    
    // Row 2: Mix and Width
    
    // Mix
    auto* mixLabel = new juce::Label("mixLabel", "Mix:");
    mixLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    mixLabel->setJustificationType(juce::Justification::right);
    mixLabel->setBounds(20, 60, 100, 24);
    addAndMakeVisible(mixLabel);
    labels.add(mixLabel);
    
    auto* mixSlider = new juce::Slider("mixSlider");
    mixSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    mixSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    mixSlider->setBounds(130, 50, 60, 60);
    addAndMakeVisible(mixSlider);
    sliders.add(mixSlider);
    
    // Width
    auto* widthLabel = new juce::Label("widthLabel", "Width:");
    widthLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    widthLabel->setJustificationType(juce::Justification::right);
    widthLabel->setBounds(200, 60, 100, 24);
    addAndMakeVisible(widthLabel);
    labels.add(widthLabel);
    
    auto* widthSlider = new juce::Slider("widthSlider");
    widthSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    widthSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    widthSlider->setBounds(310, 50, 60, 60);
    addAndMakeVisible(widthSlider);
    sliders.add(widthSlider);
    
    // Early/Late Balance
    auto* earlyLateLabel = new juce::Label("earlyLateLabel", "Early/Late:");
    earlyLateLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    earlyLateLabel->setJustificationType(juce::Justification::right);
    earlyLateLabel->setBounds(380, 60, 100, 24);
    addAndMakeVisible(earlyLateLabel);
    labels.add(earlyLateLabel);
    
    auto* earlyLateSlider = new juce::Slider("earlyLateSlider");
    earlyLateSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    earlyLateSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    earlyLateSlider->setBounds(490, 50, 60, 60);
    addAndMakeVisible(earlyLateSlider);
    sliders.add(earlyLateSlider);
    
    // Row 3: Decay and Size
    
    // Decay
    auto* decayLabel = new juce::Label("decayLabel", "Decay:");
    decayLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    decayLabel->setJustificationType(juce::Justification::right);
    decayLabel->setBounds(20, 130, 100, 24);
    addAndMakeVisible(decayLabel);
    labels.add(decayLabel);
    
    auto* decaySlider = new juce::Slider("decaySlider");
    decaySlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    decaySlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    decaySlider->setBounds(130, 120, 60, 60);
    addAndMakeVisible(decaySlider);
    sliders.add(decaySlider);
    
    // Size
    auto* sizeLabel = new juce::Label("sizeLabel", "Size:");
    sizeLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    sizeLabel->setJustificationType(juce::Justification::right);
    sizeLabel->setBounds(200, 130, 100, 24);
    addAndMakeVisible(sizeLabel);
    labels.add(sizeLabel);
    
    auto* sizeSlider = new juce::Slider("sizeSlider");
    sizeSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    sizeSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    sizeSlider->setBounds(310, 120, 60, 60);
    addAndMakeVisible(sizeSlider);
    sliders.add(sizeSlider);
    
    // Pre-Delay
    auto* preDelayLabel = new juce::Label("preDelayLabel", "Pre-Delay:");
    preDelayLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    preDelayLabel->setJustificationType(juce::Justification::right);
    preDelayLabel->setBounds(380, 130, 100, 24);
    addAndMakeVisible(preDelayLabel);
    labels.add(preDelayLabel);
    
    auto* preDelaySlider = new juce::Slider("preDelaySlider");
    preDelaySlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    preDelaySlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    preDelaySlider->setBounds(490, 120, 60, 60);
    addAndMakeVisible(preDelaySlider);
    sliders.add(preDelaySlider);
    
    // Attack
    auto* attackLabel = new juce::Label("attackLabel", "Attack:");
    attackLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    attackLabel->setJustificationType(juce::Justification::right);
    attackLabel->setBounds(560, 130, 100, 24);
    addAndMakeVisible(attackLabel);
    labels.add(attackLabel);
    
    auto* attackSlider = new juce::Slider("attackSlider");
    attackSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    attackSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    attackSlider->setBounds(670, 120, 60, 60);
    addAndMakeVisible(attackSlider);
    sliders.add(attackSlider);
    
    // Row 4: Frequency Controls
    
    // Bass Mult
    auto* bassMultLabel = new juce::Label("bassMultLabel", "Bass Mult:");
    bassMultLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    bassMultLabel->setJustificationType(juce::Justification::right);
    bassMultLabel->setBounds(20, 200, 100, 24);
    addAndMakeVisible(bassMultLabel);
    labels.add(bassMultLabel);
    
    auto* bassMultSlider = new juce::Slider("bassMultSlider");
    bassMultSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    bassMultSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    bassMultSlider->setBounds(130, 190, 60, 60);
    addAndMakeVisible(bassMultSlider);
    sliders.add(bassMultSlider);
    
    // Bass Xover
    auto* bassXoverLabel = new juce::Label("bassXoverLabel", "Bass Xover:");
    bassXoverLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    bassXoverLabel->setJustificationType(juce::Justification::right);
    bassXoverLabel->setBounds(200, 200, 100, 24);
    addAndMakeVisible(bassXoverLabel);
    labels.add(bassXoverLabel);
    
    auto* bassXoverSlider = new juce::Slider("bassXoverSlider");
    bassXoverSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    bassXoverSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    bassXoverSlider->setBounds(310, 190, 60, 60);
    addAndMakeVisible(bassXoverSlider);
    sliders.add(bassXoverSlider);
    
    // High Cut
    auto* highCutLabel = new juce::Label("highCutLabel", "High Cut:");
    highCutLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    highCutLabel->setJustificationType(juce::Justification::right);
    highCutLabel->setBounds(380, 200, 100, 24);
    addAndMakeVisible(highCutLabel);
    labels.add(highCutLabel);
    
    auto* highCutSlider = new juce::Slider("highCutSlider");
    highCutSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    highCutSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    highCutSlider->setBounds(490, 190, 60, 60);
    addAndMakeVisible(highCutSlider);
    sliders.add(highCutSlider);
    
    // Row 5: Damping and Modulation
    
    // Damping
    auto* dampingLabel = new juce::Label("dampingLabel", "Damping:");
    dampingLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    dampingLabel->setJustificationType(juce::Justification::right);
    dampingLabel->setBounds(20, 270, 100, 24);
    addAndMakeVisible(dampingLabel);
    labels.add(dampingLabel);
    
    auto* dampingSlider = new juce::Slider("dampingSlider");
    dampingSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    dampingSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    dampingSlider->setBounds(130, 260, 60, 60);
    addAndMakeVisible(dampingSlider);
    sliders.add(dampingSlider);
    
    // Damping Freq
    auto* dampingFreqLabel = new juce::Label("dampingFreqLabel", "Damp Freq:");
    dampingFreqLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    dampingFreqLabel->setJustificationType(juce::Justification::right);
    dampingFreqLabel->setBounds(200, 270, 100, 24);
    addAndMakeVisible(dampingFreqLabel);
    labels.add(dampingFreqLabel);
    
    auto* dampingFreqSlider = new juce::Slider("dampingFreqSlider");
    dampingFreqSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    dampingFreqSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    dampingFreqSlider->setBounds(310, 260, 60, 60);
    addAndMakeVisible(dampingFreqSlider);
    sliders.add(dampingFreqSlider);
    
    // Mod Rate
    auto* modRateLabel = new juce::Label("modRateLabel", "Mod Rate:");
    modRateLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    modRateLabel->setJustificationType(juce::Justification::right);
    modRateLabel->setBounds(380, 270, 100, 24);
    addAndMakeVisible(modRateLabel);
    labels.add(modRateLabel);
    
    auto* modRateSlider = new juce::Slider("modRateSlider");
    modRateSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    modRateSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    modRateSlider->setBounds(490, 260, 60, 60);
    addAndMakeVisible(modRateSlider);
    sliders.add(modRateSlider);
    
    // Mod Depth
    auto* modDepthLabel = new juce::Label("modDepthLabel", "Mod Depth:");
    modDepthLabel->setFont(juce::Font(14.0f, juce::Font::bold));
    modDepthLabel->setJustificationType(juce::Justification::right);
    modDepthLabel->setBounds(560, 270, 100, 24);
    addAndMakeVisible(modDepthLabel);
    labels.add(modDepthLabel);
    
    auto* modDepthSlider = new juce::Slider("modDepthSlider");
    modDepthSlider->setSliderStyle(juce::Slider::RotaryVerticalDrag);
    modDepthSlider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 80, 20);
    modDepthSlider->setBounds(670, 260, 60, 60);
    addAndMakeVisible(modDepthSlider);
    sliders.add(modDepthSlider);
}

void IsengardVerbAudioProcessorEditor::setupParameterAttachments()
{
    // In a real implementation, we would create SliderAttachment and 
    // ComboBoxAttachment objects to connect the UI controls to the APVTS parameters.
    // This is a placeholder for the actual implementation.
    
    // For now, we'll just set some default values
    for (auto* slider : sliders)
    {
        slider->setValue(0.5, juce::dontSendNotification);
    }
    for (auto* combo : comboBoxes)
    {
        combo->setSelectedItemIndex(0, juce::dontSendNotification);
    }
}

void IsengardVerbAudioProcessorEditor::paint(juce::Graphics& g)
{
    // Fill background
    g.fillAll(getLookAndFeel().findColour(juce::ResizableWindow::backgroundColourId));
    
    // Draw border
    g.setColour(juce::Colours::darkgrey);
    g.drawRect(0, 0, getWidth(), getHeight(), 1);
    
    // Draw title
    g.setColour(juce::Colours::white);
    g.setFont(juce::Font(24.0f, juce::Font::bold));
    g.drawText("Isengard Verb", getLocalBounds(), juce::Justification::centredTop, true);
    
    // Draw section headers
    g.setFont(juce::Font(16.0f, juce::Font::bold));
    g.setColour(juce::Colours::lightgrey);
    g.drawText("Mode & Color", 20, 45, 200, 24, juce::Justification::left);
    g.drawText("Mix & Stereo", 20, 105, 200, 24, juce::Justification::left);
    g.drawText("Reverb Core", 20, 175, 200, 24, juce::Justification::left);
    g.drawText("Frequency", 20, 245, 200, 24, juce::Justification::left);
    g.drawText("Damping & Modulation", 20, 315, 200, 24, juce::Justification::left);
}

void IsengardVerbAudioProcessorEditor::resized()
{
    // In a real implementation, we would update the bounds of all controls
    // when the editor is resized. For now, we'll just keep the fixed layout.
}
