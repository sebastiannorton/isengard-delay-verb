/**
 * Isengard Delay - Audio Plugin Processor Implementation
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#include "PluginProcessor.h"
#include "PluginEditor.h"

namespace IsengardDelay
{
    // Parameter definitions
    const juce::StringArray PARAMETER_IDS = 
    {
        "mode", "style", "mix", "feedback",
        "delay_time_ms", "delay_time_l_ms", "delay_time_r_ms", "ratio", "spread",
        "mod_rate", "mod_depth",
        "age", "drive", "diffusion", "diffusion_size",
        "eq_high", "eq_low",
        "era", "ducking", "pitch_shift", "pitch_detune", "frequency_shift"
    };
    
    const juce::StringArray PARAMETER_NAMES = 
    {
        "Mode", "Style", "Mix", "Feedback",
        "Delay Time", "Delay Time L", "Delay Time R", "Ratio", "Spread",
        "Mod Rate", "Mod Depth",
        "Age", "Drive", "Diffusion", "Diffusion Size",
        "EQ High", "EQ Low",
        "Era", "Ducking", "Pitch Shift", "Pitch Detune", "Freq Shift"
    };
    
    juce::Array<juce::NormalisableRange<float>> createParameterRanges()
    {
        juce::Array<juce::NormalisableRange<float>> ranges;
        
        // Mode (0-6)
        ranges.add(juce::NormalisableRange<float>(0.0f, 6.0f, 1.0f));
        
        // Style (0-4)
        ranges.add(juce::NormalisableRange<float>(0.0f, 4.0f, 1.0f));
        
        // Mix (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Feedback (0-0.99)
        ranges.add(juce::NormalisableRange<float>(0.0f, 0.99f));
        
        // Delay Time (1-5000ms)
        ranges.add(juce::NormalisableRange<float>(1.0f, 5000.0f));
        ranges.add(juce::NormalisableRange<float>(1.0f, 5000.0f));
        ranges.add(juce::NormalisableRange<float>(1.0f, 5000.0f));
        
        // Ratio (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Spread (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Mod Rate (0.1-10Hz)
        ranges.add(juce::NormalisableRange<float>(0.1f, 10.0f));
        
        // Mod Depth (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Age (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Drive (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Diffusion (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // EQ High (100-20000Hz)
        ranges.add(juce::NormalisableRange<float>(100.0f, 20000.0f));
        
        // EQ Low (20-1000Hz)
        ranges.add(juce::NormalisableRange<float>(20.0f, 1000.0f));
        
        // Era (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Ducking (0-1)
        ranges.add(juce::NormalisableRange<float>(0.0f, 1.0f));
        
        // Pitch Shift (-12 to 12 semitones)
        ranges.add(juce::NormalisableRange<float>(-12.0f, 12.0f));
        ranges.add(juce::NormalisableRange<float>(-12.0f, 12.0f));
        
        // Frequency Shift (-1 to 1 octaves)
        ranges.add(juce::NormalisableRange<float>(-1.0f, 1.0f));
        
        return ranges;
    }
    
    const juce::Array<juce::NormalisableRange<float>> PARAMETER_RANGES = createParameterRanges();
}

// ============================================================================
// AudioProcessor Implementation
// ============================================================================

IsengardDelayAudioProcessor::IsengardDelayAudioProcessor()
    : AudioProcessor(BusesProperties()
                     .withInput("Input", juce::AudioChannelSet::stereo(), true)
                     .withOutput("Output", juce::AudioChannelSet::stereo(), true)),
      delayProcessor(nullptr)
{
    // Create APVTS
    apvts = juce::AudioProcessorValueTreeState::create(
        *this, nullptr, "Parameters", 
        createParameterLayout()
    );
    
    // Delay processor will be created in prepareToPlay with correct sample rate
}

IsengardDelayAudioProcessor::~IsengardDelayAudioProcessor()
{
    delete delayProcessor;
}

juce::AudioProcessorValueTreeState::ParameterLayout 
IsengardDelayAudioProcessor::createParameterLayout()
{
    juce::AudioProcessorValueTreeState::ParameterLayout layout;
    
    // Add all parameters
    for (int i = 0; i < IsengardDelay::kNumParameters; ++i)
    {
        auto range = IsengardDelay::PARAMETER_RANGES.getReference(i);
        
        if (i == kParamMode || i == kParamStyle)
        {
            // Discrete parameters (combo boxes)
            layout.add(std::make_unique<juce::AudioParameterChoice>(
                IsengardDelay::PARAMETER_IDS[i],
                IsengardDelay::PARAMETER_NAMES[i],
                (i == kParamMode) ? 
                    juce::StringArray({"Tape", "HiFi", "BBD", "Digital", "Ghost", "Pitch", "RevPitch"}) :
                    juce::StringArray({"Single", "Dual", "Ratio", "PingPong", "Quad"}),
                (i == kParamMode) ? 0 : 0
            ));
        }
        else
        {
            // Continuous parameters (sliders)
            layout.add(std::make_unique<juce::AudioParameterFloat>(
                IsengardDelay::PARAMETER_IDS[i],
                IsengardDelay::PARAMETER_NAMES[i],
                range,
                (i == kParamMix || i == kParamFeedback) ? 0.5f : 
                (i == kParamDelayTimeMs) ? 500.0f :
                (i == kParamModRate) ? 0.5f :
                (i == kParamModDepth) ? 0.1f : 0.0f
            ));
        }
    }
    
    return layout;
}

void IsengardDelayAudioProcessor::prepareToPlay(double sampleRate, int samplesPerBlock)
{
    this->sampleRate = sampleRate;
    this->samplesPerBlock = samplesPerBlock;
    
    // Create delay processor with correct sample rate
    delete delayProcessor;
    delayProcessor = new Isengard::DelayProcessor(sampleRate);
    
    // Set default mode and style
    delayProcessor->setMode("tape");
    delayProcessor->setStyle("single");
    
    // Set default parameters
    delayProcessor->setParameters({
        {"mix", 0.5f},
        {"feedback", 0.5f},
        {"delay_time_ms", 500.0f}
    });
}

void IsengardDelayAudioProcessor::releaseResources()
{
    delete delayProcessor;
    delayProcessor = nullptr;
}

void IsengardDelayAudioProcessor::processBlock(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
{
    juce::ScopedNoDenormals noDenormals;
    
    // Get parameters from APVTS
    updateParameters();
    
    // Process each channel
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
        auto [outL, outR] = delayProcessor->processSample(leftInput[i], rightInput[i]);
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

void IsengardDelayAudioProcessor::updateParameters()
{
    // Get all parameter values from APVTS
    // This is a simplified version - in a real implementation, 
    // we would use AudioProcessorValueTreeState::SliderAttachment
    
    // For now, we'll just update the delay processor with some default values
    // A full implementation would use proper parameter attachments
}

void IsengardDelayAudioProcessor::setMode(int modeIndex)
{
    const juce::StringArray modes = {"tape", "hifi", "bbd", "digital", "ghost", "pitch", "revpitch"};
    if (modeIndex >= 0 && modeIndex < modes.size())
    {
        delayProcessor->setMode(modes[modeIndex]);
    }
}

void IsengardDelayAudioProcessor::setStyle(int styleIndex)
{
    const juce::StringArray styles = {"single", "dual", "ratio", "pingpong", "quad"};
    if (styleIndex >= 0 && styleIndex < styles.size())
    {
        delayProcessor->setStyle(styles[styleIndex]);
    }
}

// ============================================================================
// AudioProcessor Info
// ============================================================================

const juce::String IsengardDelayAudioProcessor::getName() const
{
    return JucePlugin_Name;
}

bool IsengardDelayAudioProcessor::acceptsMidi() const
{
    return false;
}

bool IsengardDelayAudioProcessor::producesMidi() const
{
    return false;
}

double IsengardDelayAudioProcessor::getTailLengthSeconds() const
{
    return 0.0;
}

int IsengardDelayAudioProcessor::getNumPrograms()
{
    return 0; // No programs - we use parameter automation
}

int IsengardDelayAudioProcessor::getCurrentProgram()
{
    return 0;
}

void IsengardDelayAudioProcessor::setCurrentProgram(int index)
{
}

const juce::String IsengardDelayAudioProcessor::getProgramName(int index)
{
    return {};
}

void IsengardDelayAudioProcessor::changeProgramName(int index, const juce::String& newName)
{
}

bool IsengardDelayAudioProcessor::hasEditor() const
{
    return true;
}

juce::AudioProcessorEditor* IsengardDelayAudioProcessor::createEditor()
{
    return new IsengardDelayAudioProcessorEditor(*this);
}

// ============================================================================
// State Management
// ============================================================================

void IsengardDelayAudioProcessor::getStateInformation(juce::MemoryBlock& destData)
{
    // Save APVTS state
    std::unique_ptr<juce::XmlElement> xml(apvts.copyState());
    copyXmlToBinary(*xml, destData);
}

void IsengardDelayAudioProcessor::setStateInformation(const void* data, int sizeInBytes)
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
    return new IsengardDelayAudioProcessor();
}
