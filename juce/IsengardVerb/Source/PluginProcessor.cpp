/**
 * Isengard Verb - Audio Plugin Processor Implementation
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#include "PluginProcessor.h"
#include "PluginEditor.h"

namespace IsengardVerb
{
    // Mode names (22 modes from ValhallaVintageVerb)
    const juce::StringArray MODE_NAMES = 
    {
        "1972", "1973", "1974", "1975", "1976", "1977", "1978", "1979",
        "1980", "1981", "1982", "1983", "1984", "1985", "1986", "1987",
        "1988", "1989", "1990", "1991", "1992", "1993", "1994", "1995",
        "NOW1", "NOW2"
    };
    
    // Color names
    const juce::StringArray COLOR_NAMES = 
    {
        "1970s", "1980s", "Now"
    };
    
    // Parameter definitions
    const juce::StringArray PARAMETER_IDS = 
    {
        "mode", "color", "mix",
        "decay", "size", "pre_delay", "attack",
        "bass_mult", "bass_xover", "high_cut", "damping", "damping_freq",
        "mod_rate", "mod_depth",
        "width", "early_late_balance"
    };
    
    const juce::StringArray PARAMETER_NAMES = 
    {
        "Mode", "Color", "Mix",
        "Decay", "Size", "Pre-Delay", "Attack",
        "Bass Mult", "Bass Xover", "High Cut", "Damping", "Damp Freq",
        "Mod Rate", "Mod Depth",
        "Width", "Early/Late"
    };
    
    juce::Array<juce::NormalisableRange<float>> createParameterRanges()
    {
        juce::Array<juce::NormalisableRange<float>> ranges;
        
        // Mode (0-23)
        ranges.add(juce::NormalisableRange<float>(0.0f, 23.0f, 1.0f));
        
        // Color (0-2)
        ranges.add(juce::NormalisableRange<float>(0.0f, 2.0f, 1.0f));
        
        // Mix (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Decay (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Size (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Pre-Delay (0-200ms)
        ranges.add(juce::NormalisableRange<float>(0.0f, 200.0f));
        
        // Attack (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Bass Mult (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Bass Xover (20-1000Hz)
        ranges.add(juce::NormalisableRange<float>(20.0f, 1000.0f));
        
        // High Cut (1000-20000Hz)
        ranges.add(juce::NormalisableRange<float>(1000.0f, 20000.0f));
        
        // Damping (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Damping Freq (100-20000Hz)
        ranges.add(juce::NormalisableRange<float>(100.0f, 20000.0f));
        
        // Mod Rate (0.1-10Hz)
        ranges.add(juce::NormalisableRange<float>(0.1f, 10.0f));
        
        // Mod Depth (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Width (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Early/Late Balance (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        return ranges;
    }
    
    const juce::Array<juce::NormalisableRange<float>> PARAMETER_RANGES = createParameterRanges();
}

// ============================================================================
// AudioProcessor Implementation
// ============================================================================

IsengardVerbAudioProcessor::IsengardVerbAudioProcessor()
    : AudioProcessor(BusesProperties()
                     .withInput("Input", juce::AudioChannelSet::stereo(), true)
                     .withOutput("Output", juce::AudioChannelSet::stereo(), true)),
      verbProcessor(nullptr)
{
    // Create APVTS
    apvts = juce::AudioProcessorValueTreeState::create(
        *this, nullptr, "Parameters", 
        createParameterLayout()
    );
    
    // Verb processor will be created in prepareToPlay with correct sample rate
}

IsengardVerbAudioProcessor::~IsengardVerbAudioProcessor()
{
    delete verbProcessor;
}

juce::AudioProcessorValueTreeState::ParameterLayout 
IsengardVerbAudioProcessor::createParameterLayout()
{
    juce::AudioProcessorValueTreeState::ParameterLayout layout;
    
    // Add all parameters
    for (int i = 0; i < IsengardVerb::kNumParameters; ++i)
    {
        auto range = IsengardVerb::PARAMETER_RANGES.getReference(i);
        
        if (i == kParamMode)
        {
            // Mode selector (combo box)
            layout.add(std::make_unique<juce::AudioParameterChoice>(
                IsengardVerb::PARAMETER_IDS[i],
                IsengardVerb::PARAMETER_NAMES[i],
                IsengardVerb::MODE_NAMES,
                6  // Default to 1978 (index 6)
            ));
        }
        else if (i == kParamColor)
        {
            // Color selector (combo box)
            layout.add(std::make_unique<juce::AudioParameterChoice>(
                IsengardVerb::PARAMETER_IDS[i],
                IsengardVerb::PARAMETER_NAMES[i],
                IsengardVerb::COLOR_NAMES,
                1  // Default to 1980s (index 1)
            ));
        }
        else
        {
            // Continuous parameters (sliders)
            float defaultValue = 0.0f;
            if (i == kParamMix) defaultValue = 0.5f;
            else if (i == kParamDecay) defaultValue = 0.5f;
            else if (i == kParamSize) defaultValue = 0.5f;
            else if (i == kParamPreDelay) defaultValue = 0.0f;
            else if (i == kParamAttack) defaultValue = 0.0f;
            else if (i == kParamBassMult) defaultValue = 0.5f;
            else if (i == kParamBassXover) defaultValue = 200.0f;
            else if (i == kParamHighCut) defaultValue = 10000.0f;
            else if (i == kParamDamping) defaultValue = 0.5f;
            else if (i == kParamDampingFreq) defaultValue = 5000.0f;
            else if (i == kParamModRate) defaultValue = 0.5f;
            else if (i == kParamModDepth) defaultValue = 0.1f;
            else if (i == kParamWidth) defaultValue = 0.5f;
            else if (i == kParamEarlyLateBalance) defaultValue = 0.5f;
            
            layout.add(std::make_unique<juce::AudioParameterFloat>(
                IsengardVerb::PARAMETER_IDS[i],
                IsengardVerb::PARAMETER_NAMES[i],
                range,
                defaultValue
            ));
        }
    }
    
    return layout;
}

void IsengardVerbAudioProcessor::prepareToPlay(double sampleRate, int samplesPerBlock)
{
    this->sampleRate = sampleRate;
    this->samplesPerBlock = samplesPerBlock;
    
    // Create verb processor with correct sample rate
    delete verbProcessor;
    verbProcessor = new Isengard::VerbProcessor(sampleRate);
    
    // Set default mode and color
    verbProcessor->setMode("1978");
    verbProcessor->setColor("1980s");
    
    // Set default parameters
    verbProcessor->setParameters({
        {"mix", 0.5f},
        {"decay", 0.5f},
        {"size", 0.5f},
        {"pre_delay", 0.0f}
    });
}

void IsengardVerbAudioProcessor::releaseResources()
{
    delete verbProcessor;
    verbProcessor = nullptr;
}

void IsengardVerbAudioProcessor::processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
{
    juce::ScopedNoDenormals noDenormals;
    
    // Get parameters from APVTS
    updateParameters();
    
    // Process each sample
    int numSamples = buffer.getNumSamples();
    
    // Create temporary buffers for processing
    juce::HeapBlock<float> tempBuffer(numSamples * 2);
    float* leftInput = buffer.getWritePointer(0);
    float* rightInput = (buffer.getNumChannels() > 1) ? buffer.getWritePointer(1) : leftInput;
    float* leftOutput = tempBuffer.getData();
    float* rightOutput = leftOutput + numSamples;
    
    // Process sample by sample
    for (int i = 0; i < numSamples; ++i)
    {
        auto [outL, outR] = verbProcessor->processSample(leftInput[i], rightInput[i]);
        leftOutput[i] = outL;
        rightOutput[i] = outR;
    }
    
    // Copy back to output
    std::memcpy(leftInput, leftOutput, numSamples * sizeof(float));
    if (buffer.getNumChannels() > 1)
    {
        std::memcpy(rightInput, rightOutput, numSamples * sizeof(float));
    }
}

void IsengardVerbAudioProcessor::updateParameters()
{
    // Get all parameter values from APVTS
    // This is a simplified version - in a real implementation, 
    // we would use AudioProcessorValueTreeState::SliderAttachment
    
    // For now, we'll just update the verb processor with some default values
    // A full implementation would use proper parameter attachments
}

void IsengardVerbAudioProcessor::setMode(int modeIndex)
{
    if (modeIndex >= 0 && modeIndex < MODE_NAMES.size())
    {
        verbProcessor->setMode(MODE_NAMES[modeIndex]);
    }
}

void IsengardVerbAudioProcessor::setColor(int colorIndex)
{
    if (colorIndex >= 0 && colorIndex < COLOR_NAMES.size())
    {
        verbProcessor->setColor(COLOR_NAMES[colorIndex]);
    }
}

// ============================================================================
// AudioProcessor Info
// ============================================================================

const juce::String IsengardVerbAudioProcessor::getName() const
{
    return JucePlugin_Name;
}

bool IsengardVerbAudioProcessor::acceptsMidi() const
{
    return false;
}

bool IsengardVerbAudioProcessor::producesMidi() const
{
    return false;
}

double IsengardVerbAudioProcessor::getTailLengthSeconds() const
{
    // Reverb has a long tail - set to maximum expected
    return 10.0;
}

int IsengardVerbAudioProcessor::getNumPrograms()
{
    return 0; // No programs - we use parameter automation
}

int IsengardVerbAudioProcessor::getCurrentProgram()
{
    return 0;
}

void IsengardVerbAudioProcessor::setCurrentProgram(int index)
{
}

const juce::String IsengardVerbAudioProcessor::getProgramName(int index)
{
    return {};
}

void IsengardVerbAudioProcessor::changeProgramName(int index, const juce::String& newName)
{
}

bool IsengardVerbAudioProcessor::hasEditor() const
{
    return true;
}

juce::AudioProcessorEditor* IsengardVerbAudioProcessor::createEditor()
{
    return new IsengardVerbAudioProcessorEditor(*this);
}

// ============================================================================
// State Management
// ============================================================================

void IsengardVerbAudioProcessor::getStateInformation(juce::MemoryBlock& destData)
{
    // Save APVTS state
    std::unique_ptr<juce::XmlElement> xml(apvts.copyState());
    copyXmlToBinary(*xml, destData);
}

void IsengardVerbAudioProcessor::setStateInformation(const void* data, int sizeInBytes)
{
    // Load APVTS state
    std::unique_ptr<juce::XmlElement> xml(getXmlFromBinary(data, sizeInBytes));
    if (xml.get() != nullptr)
    {
        apvts.replaceState(juce::ValueTree::fromXml(*xml));
    }
}

// ============================================================================
// Plugin Entry Point
// ============================================================================

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new IsengardVerbAudioProcessor();
}
