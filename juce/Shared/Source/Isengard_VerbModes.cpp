/**
 * Isengard Verb Modes Implementation
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#include "Isengard_VerbModes.h"
#include "Isengard_FDN.h"

namespace Isengard
{
    // ============================================================================
    // VerbModeBase Implementation
    // ============================================================================
    
    VerbModeBase::VerbModeBase(double sampleRate)
        : sampleRate(sampleRate)
    {
    }
    
    VerbModeBase::~VerbModeBase()
    {
    }
    
    void VerbModeBase::setSampleRate(double sampleRate)
    {
        this->sampleRate = sampleRate;
    }
    
    void VerbModeBase::setParameter(const juce::String& paramName, float value)
    {
        // Base implementation does nothing
    }
    
    void VerbModeBase::reset()
    {
    }
    
    void VerbModeBase::configureEarlyReflections(EarlyReflections* er)
    {
        // Base implementation does nothing
    }
    
    void VerbModeBase::configureModulation(ModulationMatrix* mod)
    {
        // Base implementation does nothing
    }
    
    // ============================================================================
    // Mode Configuration Structures
    // ============================================================================
    
    struct ModeConfig
    {
        const char* name;
        float combDelaysMs[4];    // Delay times for 4 comb filters
        float combFeedbacks[4];   // Feedback amounts for 4 comb filters
        float allpassDelaysMs[2]; // Delay times for 2 allpass filters
        float allpassFeedbacks[2];// Feedback amounts for 2 allpass filters
        float decayScale;          // Decay scaling factor
        float sizeScale;           // Size scaling factor
        float diffusion;           // Diffusion amount
        float damping;             // Damping amount
        float modRate;             // Modulation rate
        float modDepth;            // Modulation depth
    };
    
    // Mode configurations based on ValhallaVintageVerb analysis
    // These are simplified configurations - in a full implementation, 
    // each mode would have its own class with detailed parameter mappings
    
    static const ModeConfig modeConfigs[] = {
        // 1970s modes
        {
            "1972",
            {1423.0f, 1687.0f, 2159.0f, 2849.0f},  // EMT 140 Plate - long, dense
            {0.85f, 0.82f, 0.79f, 0.76f},
            {149.0f, 211.0f},
            {0.7f, 0.7f},
            1.0f, 1.0f, 0.6f, 0.4f, 0.3f, 0.1f
        },
        {
            "1974",
            {1237.0f, 1493.0f, 1871.0f, 2357.0f},  // AMS RMX16 - medium plate
            {0.84f, 0.81f, 0.78f, 0.75f},
            {131.0f, 181.0f},
            {0.7f, 0.7f},
            0.95f, 0.9f, 0.65f, 0.45f, 0.35f, 0.12f
        },
        {
            "1975",
            {1123.0f, 1379.0f, 1687.0f, 2131.0f},  // Eventide SP2016 - room
            {0.83f, 0.80f, 0.77f, 0.74f},
            {113.0f, 163.0f},
            {0.7f, 0.7f},
            0.9f, 0.85f, 0.7f, 0.5f, 0.4f, 0.15f
        },
        {
            "1976",
            {1019.0f, 1277.0f, 1597.0f, 2039.0f},  // EMT 250 - hall
            {0.82f, 0.79f, 0.76f, 0.73f},
            {101.0f, 151.0f},
            {0.7f, 0.7f},
            0.85f, 0.8f, 0.75f, 0.55f, 0.45f, 0.18f
        },
        {
            "1977",
            {923.0f, 1159.0f, 1453.0f, 1859.0f},   // Quantec - room simulator
            {0.81f, 0.78f, 0.75f, 0.72f},
            {91.0f, 141.0f},
            {0.7f, 0.7f},
            0.8f, 0.75f, 0.8f, 0.6f, 0.5f, 0.2f
        },
        {
            "1978",
            {839.0f, 1051.0f, 1319.0f, 1709.0f},   // Lexicon 224 - classic
            {0.80f, 0.77f, 0.74f, 0.71f},
            {83.0f, 133.0f},
            {0.7f, 0.7f},
            0.75f, 0.7f, 0.85f, 0.65f, 0.55f, 0.22f
        },
        {
            "1979",
            {767.0f, 961.0f, 1207.0f, 1567.0f},    // AMS RMX16 variant
            {0.79f, 0.76f, 0.73f, 0.70f},
            {77.0f, 127.0f},
            {0.7f, 0.7f},
            0.7f, 0.65f, 0.9f, 0.7f, 0.6f, 0.25f
        },
        
        // 1980s modes
        {
            "1980",
            {697.0f, 877.0f, 1109.0f, 1447.0f},    // Lexicon 224X
            {0.78f, 0.75f, 0.72f, 0.69f},
            {69.0f, 119.0f},
            {0.7f, 0.7f},
            0.65f, 0.6f, 0.95f, 0.75f, 0.65f, 0.28f
        },
        {
            "1981",
            {631.0f, 797.0f, 1009.0f, 1307.0f},    // Yamaha Rev1
            {0.77f, 0.74f, 0.71f, 0.68f},
            {63.0f, 113.0f},
            {0.7f, 0.7f},
            0.6f, 0.55f, 1.0f, 0.8f, 0.7f, 0.3f
        },
        {
            "1982",
            {571.0f, 719.0f, 919.0f, 1183.0f},      // Sony DRP-F300
            {0.76f, 0.73f, 0.70f, 0.67f},
            {57.0f, 107.0f},
            {0.7f, 0.7f},
            0.55f, 0.5f, 1.05f, 0.85f, 0.75f, 0.32f
        },
        {
            "1983",
            {517.0f, 653.0f, 833.0f, 1069.0f},      // AKG ADR68K
            {0.75f, 0.72f, 0.69f, 0.66f},
            {52.0f, 102.0f},
            {0.7f, 0.7f},
            0.5f, 0.45f, 1.1f, 0.9f, 0.8f, 0.35f
        },
        {
            "1984",
            {467.0f, 593.0f, 761.0f, 979.0f},       // Roland SRV-2000
            {0.74f, 0.71f, 0.68f, 0.65f},
            {47.0f, 97.0f},
            {0.7f, 0.7f},
            0.45f, 0.4f, 1.15f, 0.95f, 0.85f, 0.38f
        },
        {
            "1985",
            {421.0f, 539.0f, 697.0f, 893.0f},       // Lexicon 300
            {0.73f, 0.70f, 0.67f, 0.64f},
            {42.0f, 92.0f},
            {0.7f, 0.7f},
            0.4f, 0.35f, 1.2f, 1.0f, 0.9f, 0.4f
        },
        {
            "1986",
            {379.0f, 487.0f, 631.0f, 817.0f},       // Yamaha Rev5
            {0.72f, 0.69f, 0.66f, 0.63f},
            {38.0f, 88.0f},
            {0.7f, 0.7f},
            0.35f, 0.3f, 1.25f, 1.05f, 0.95f, 0.42f
        },
        {
            "1987",
            {343.0f, 443.0f, 571.0f, 737.0f},       // Lexicon 480L
            {0.71f, 0.68f, 0.65f, 0.62f},
            {34.0f, 84.0f},
            {0.7f, 0.7f},
            0.3f, 0.25f, 1.3f, 1.1f, 1.0f, 0.45f
        },
        
        // 1990s modes
        {
            "1990",
            {307.0f, 397.0f, 511.0f, 661.0f},       // Lexicon PCM70
            {0.70f, 0.67f, 0.64f, 0.61f},
            {31.0f, 81.0f},
            {0.7f, 0.7f},
            0.25f, 0.2f, 1.35f, 1.15f, 1.05f, 0.48f
        },
        {
            "1991",
            {277.0f, 359.0f, 461.0f, 599.0f},       // Yamaha Rev7
            {0.69f, 0.66f, 0.63f, 0.60f},
            {28.0f, 78.0f},
            {0.7f, 0.7f},
            0.2f, 0.15f, 1.4f, 1.2f, 1.1f, 0.5f
        },
        {
            "1992",
            {247.0f, 323.0f, 421.0f, 547.0f},       // Eventide H3000
            {0.68f, 0.65f, 0.62f, 0.59f},
            {25.0f, 75.0f},
            {0.7f, 0.7f},
            0.15f, 0.1f, 1.45f, 1.25f, 1.15f, 0.52f
        },
        {
            "1993",
            {223.0f, 291.0f, 383.0f, 499.0f},       // TC Electronic M3000
            {0.67f, 0.64f, 0.61f, 0.58f},
            {22.0f, 72.0f},
            {0.7f, 0.7f},
            0.1f, 0.05f, 1.5f, 1.3f, 1.2f, 0.55f
        },
        {
            "1994",
            {203.0f, 269.0f, 353.0f, 461.0f},       // Lexicon PCM80
            {0.66f, 0.63f, 0.60f, 0.57f},
            {20.0f, 70.0f},
            {0.7f, 0.7f},
            0.05f, 0.0f, 1.55f, 1.35f, 1.25f, 0.58f
        },
        {
            "1995",
            {187.0f, 247.0f, 329.0f, 433.0f},       // Yamaha SPX90
            {0.65f, 0.62f, 0.59f, 0.56f},
            {19.0f, 68.0f},
            {0.7f, 0.7f},
            0.0f, 0.0f, 1.6f, 1.4f, 1.3f, 0.6f
        },
        
        // NOW modes
        {
            "NOW1",
            {167.0f, 223.0f, 297.0f, 391.0f},       // Modern Algorithm 1
            {0.64f, 0.61f, 0.58f, 0.55f},
            {17.0f, 66.0f},
            {0.7f, 0.7f},
            0.0f, 0.0f, 1.65f, 1.45f, 1.35f, 0.62f
        },
        {
            "NOW2",
            {151.0f, 209.0f, 283.0f, 373.0f},       // Modern Algorithm 2
            {0.63f, 0.60f, 0.57f, 0.54f},
            {15.0f, 64.0f},
            {0.7f, 0.7f},
            0.0f, 0.0f, 1.7f, 1.5f, 1.4f, 0.65f
        }
    };
    
    // ============================================================================
    // Mode Implementations
    // ============================================================================
    
    // 1972 - EMT 140 Plate
    Mode1972::Mode1972(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1972::~Mode1972() {}
    void Mode1972::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[0];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1974 - AMS RMX16
    Mode1974::Mode1974(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1974::~Mode1974() {}
    void Mode1974::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[1];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1975 - Eventide SP2016
    Mode1975::Mode1975(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1975::~Mode1975() {}
    void Mode1975::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[2];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1976 - EMT 250
    Mode1976::Mode1976(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1976::~Mode1976() {}
    void Mode1976::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[3];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1977 - Quantec
    Mode1977::Mode1977(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1977::~Mode1977() {}
    void Mode1977::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[4];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1978 - Lexicon 224
    Mode1978::Mode1978(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1978::~Mode1978() {}
    void Mode1978::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[5];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1979 - AMS RMX16 Variant
    Mode1979::Mode1979(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1979::~Mode1979() {}
    void Mode1979::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[6];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1980 - Lexicon 224X
    Mode1980::Mode1980(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1980::~Mode1980() {}
    void Mode1980::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[7];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1981 - Yamaha Rev1
    Mode1981::Mode1981(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1981::~Mode1981() {}
    void Mode1981::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[8];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1982 - Sony DRP-F300
    Mode1982::Mode1982(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1982::~Mode1982() {}
    void Mode1982::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[9];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1983 - AKG ADR68K
    Mode1983::Mode1983(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1983::~Mode1983() {}
    void Mode1983::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[10];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1984 - Roland SRV-2000
    Mode1984::Mode1984(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1984::~Mode1984() {}
    void Mode1984::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[11];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1985 - Lexicon 300
    Mode1985::Mode1985(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1985::~Mode1985() {}
    void Mode1985::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[12];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1986 - Yamaha Rev5
    Mode1986::Mode1986(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1986::~Mode1986() {}
    void Mode1986::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[13];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1987 - Lexicon 480L
    Mode1987::Mode1987(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1987::~Mode1987() {}
    void Mode1987::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[14];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1990 - Lexicon PCM70
    Mode1990::Mode1990(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1990::~Mode1990() {}
    void Mode1990::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[15];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1991 - Yamaha Rev7
    Mode1991::Mode1991(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1991::~Mode1991() {}
    void Mode1991::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[16];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1992 - Eventide H3000
    Mode1992::Mode1992(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1992::~Mode1992() {}
    void Mode1992::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[17];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1993 - TC Electronic M3000
    Mode1993::Mode1993(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1993::~Mode1993() {}
    void Mode1993::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[18];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1994 - Lexicon PCM80
    Mode1994::Mode1994(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1994::~Mode1994() {}
    void Mode1994::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[19];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // 1995 - Yamaha SPX90
    Mode1995::Mode1995(double sampleRate) : VerbModeBase(sampleRate) {}
    Mode1995::~Mode1995() {}
    void Mode1995::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[20];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // NOW1 - Modern Algorithm 1
    ModeNOW1::ModeNOW1(double sampleRate) : VerbModeBase(sampleRate) {}
    ModeNOW1::~ModeNOW1() {}
    void ModeNOW1::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[21];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // NOW2 - Modern Algorithm 2
    ModeNOW2::ModeNOW2(double sampleRate) : VerbModeBase(sampleRate) {}
    ModeNOW2::~ModeNOW2() {}
    void ModeNOW2::configureFDN(FDNReverb* fdn)
    {
        if (!fdn) return;
        const ModeConfig& config = modeConfigs[22];
        fdn->setCombDelays(config.combDelaysMs, 4);
        fdn->setCombFeedbacks(config.combFeedbacks, 4);
        fdn->setAllpassDelays(config.allpassDelaysMs, 2);
        fdn->setAllpassFeedbacks(config.allpassFeedbacks, 2);
        fdn->setDecay(0.5f * config.decayScale);
        fdn->setDiffusion(config.diffusion);
        fdn->setDamping(config.damping);
        fdn->setModRate(config.modRate);
        fdn->setModDepth(config.modDepth);
    }
    
    // ============================================================================
    // Mode Factory
    // ============================================================================
    
    VerbModeBase* createVerbMode(Isengard::VerbMode mode, double sampleRate)
    {
        switch (mode)
        {
            case Isengard::VerbMode::MODE_1972: return new Mode1972(sampleRate);
            case Isengard::VerbMode::MODE_1974: return new Mode1974(sampleRate);
            case Isengard::VerbMode::MODE_1975: return new Mode1975(sampleRate);
            case Isengard::VerbMode::MODE_1976: return new Mode1976(sampleRate);
            case Isengard::VerbMode::MODE_1977: return new Mode1977(sampleRate);
            case Isengard::VerbMode::MODE_1978: return new Mode1978(sampleRate);
            case Isengard::VerbMode::MODE_1979: return new Mode1979(sampleRate);
            case Isengard::VerbMode::MODE_1980: return new Mode1980(sampleRate);
            case Isengard::VerbMode::MODE_1981: return new Mode1981(sampleRate);
            case Isengard::VerbMode::MODE_1982: return new Mode1982(sampleRate);
            case Isengard::VerbMode::MODE_1983: return new Mode1983(sampleRate);
            case Isengard::VerbMode::MODE_1984: return new Mode1984(sampleRate);
            case Isengard::VerbMode::MODE_1985: return new Mode1985(sampleRate);
            case Isengard::VerbMode::MODE_1986: return new Mode1986(sampleRate);
            case Isengard::VerbMode::MODE_1987: return new Mode1987(sampleRate);
            case Isengard::VerbMode::MODE_1990: return new Mode1990(sampleRate);
            case Isengard::VerbMode::MODE_1991: return new Mode1991(sampleRate);
            case Isengard::VerbMode::MODE_1992: return new Mode1992(sampleRate);
            case Isengard::VerbMode::MODE_1993: return new Mode1993(sampleRate);
            case Isengard::VerbMode::MODE_1994: return new Mode1994(sampleRate);
            case Isengard::VerbMode::MODE_1995: return new Mode1995(sampleRate);
            case Isengard::VerbMode::MODE_NOW1: return new ModeNOW1(sampleRate);
            case Isengard::VerbMode::MODE_NOW2: return new ModeNOW2(sampleRate);
            default: return new Mode1978(sampleRate);
        }
    }
    
    VerbModeBase* createVerbMode(const juce::String& modeName, double sampleRate)
    {
        juce::String lowerName = modeName.toLowerCase();
        
        if (lowerName == "1972") return new Mode1972(sampleRate);
        if (lowerName == "1974") return new Mode1974(sampleRate);
        if (lowerName == "1975") return new Mode1975(sampleRate);
        if (lowerName == "1976") return new Mode1976(sampleRate);
        if (lowerName == "1977") return new Mode1977(sampleRate);
        if (lowerName == "1978") return new Mode1978(sampleRate);
        if (lowerName == "1979") return new Mode1979(sampleRate);
        if (lowerName == "1980") return new Mode1980(sampleRate);
        if (lowerName == "1981") return new Mode1981(sampleRate);
        if (lowerName == "1982") return new Mode1982(sampleRate);
        if (lowerName == "1983") return new Mode1983(sampleRate);
        if (lowerName == "1984") return new Mode1984(sampleRate);
        if (lowerName == "1985") return new Mode1985(sampleRate);
        if (lowerName == "1986") return new Mode1986(sampleRate);
        if (lowerName == "1987") return new Mode1987(sampleRate);
        if (lowerName == "1990") return new Mode1990(sampleRate);
        if (lowerName == "1991") return new Mode1991(sampleRate);
        if (lowerName == "1992") return new Mode1992(sampleRate);
        if (lowerName == "1993") return new Mode1993(sampleRate);
        if (lowerName == "1994") return new Mode1994(sampleRate);
        if (lowerName == "1995") return new Mode1995(sampleRate);
        if (lowerName == "now1") return new ModeNOW1(sampleRate);
        if (lowerName == "now2") return new ModeNOW2(sampleRate);
        
        return new Mode1978(sampleRate);
    }
}
