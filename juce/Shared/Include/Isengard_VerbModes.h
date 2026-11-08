/**
 * Isengard Verb Modes
 * 
 * Implementations for all 22 verb modes based on ValhallaVintageVerb.
 * 
 * Copyright (c) 2024 Isengard Audio
 */

#pragma once

#include <JuceHeader.h>

namespace Isengard
{
    // Verb Mode enum (independent to avoid circular dependency)
    enum class VerbMode
    {
        MODE_1972,
        MODE_1974,
        MODE_1975,
        MODE_1976,
        MODE_1977,
        MODE_1978,
        MODE_1979,
        MODE_1980,
        MODE_1981,
        MODE_1982,
        MODE_1983,
        MODE_1984,
        MODE_1985,
        MODE_1986,
        MODE_1987,
        MODE_1990,
        MODE_1991,
        MODE_1992,
        MODE_1993,
        MODE_1994,
        MODE_1995,
        MODE_NOW1,
        MODE_NOW2,
        NUM_MODES
    };
    
    // Forward declarations
    class FDNReverb;
    class EarlyReflections;
    class ModulationMatrix;
    
    /**
     * Base class for all verb modes.
     * 
     * Each mode configures the FDN reverb with specific parameters
     * for a particular vintage reverb sound.
     */
    class VerbModeBase
    {
    public:
        VerbModeBase(double sampleRate);
        virtual ~VerbModeBase();
        
        virtual void configureFDN(FDNReverb* fdn) = 0;
        virtual void configureEarlyReflections(EarlyReflections* er);
        virtual void configureModulation(ModulationMatrix* mod);
        
        virtual void setSampleRate(double sampleRate);
        virtual void setParameter(const juce::String& paramName, float value);
        virtual void reset();
        
        virtual juce::String getName() const = 0;
        
    protected:
        double sampleRate;
    };
    
    // ============================================================================
    // 1970s Modes
    // ============================================================================
    
    class Mode1972 : public VerbModeBase
    {
    public:
        Mode1972(double sampleRate);
        ~Mode1972() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1972"; }
    };
    
    class Mode1974 : public VerbModeBase
    {
    public:
        Mode1974(double sampleRate);
        ~Mode1974() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1974"; }
    };
    
    class Mode1975 : public VerbModeBase
    {
    public:
        Mode1975(double sampleRate);
        ~Mode1975() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1975"; }
    };
    
    class Mode1976 : public VerbModeBase
    {
    public:
        Mode1976(double sampleRate);
        ~Mode1976() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1976"; }
    };
    
    class Mode1977 : public VerbModeBase
    {
    public:
        Mode1977(double sampleRate);
        ~Mode1977() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1977"; }
    };
    
    class Mode1978 : public VerbModeBase
    {
    public:
        Mode1978(double sampleRate);
        ~Mode1978() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1978"; }
    };
    
    class Mode1979 : public VerbModeBase
    {
    public:
        Mode1979(double sampleRate);
        ~Mode1979() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1979"; }
    };
    
    // ============================================================================
    // 1980s Modes
    // ============================================================================
    
    class Mode1980 : public VerbModeBase
    {
    public:
        Mode1980(double sampleRate);
        ~Mode1980() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1980"; }
    };
    
    class Mode1981 : public VerbModeBase
    {
    public:
        Mode1981(double sampleRate);
        ~Mode1981() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1981"; }
    };
    
    class Mode1982 : public VerbModeBase
    {
    public:
        Mode1982(double sampleRate);
        ~Mode1982() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1982"; }
    };
    
    class Mode1983 : public VerbModeBase
    {
    public:
        Mode1983(double sampleRate);
        ~Mode1983() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1983"; }
    };
    
    class Mode1984 : public VerbModeBase
    {
    public:
        Mode1984(double sampleRate);
        ~Mode1984() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1984"; }
    };
    
    class Mode1985 : public VerbModeBase
    {
    public:
        Mode1985(double sampleRate);
        ~Mode1985() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1985"; }
    };
    
    class Mode1986 : public VerbModeBase
    {
    public:
        Mode1986(double sampleRate);
        ~Mode1986() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1986"; }
    };
    
    class Mode1987 : public VerbModeBase
    {
    public:
        Mode1987(double sampleRate);
        ~Mode1987() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1987"; }
    };
    
    // ============================================================================
    // 1990s Modes
    // ============================================================================
    
    class Mode1990 : public VerbModeBase
    {
    public:
        Mode1990(double sampleRate);
        ~Mode1990() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1990"; }
    };
    
    class Mode1991 : public VerbModeBase
    {
    public:
        Mode1991(double sampleRate);
        ~Mode1991() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1991"; }
    };
    
    class Mode1992 : public VerbModeBase
    {
    public:
        Mode1992(double sampleRate);
        ~Mode1992() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1992"; }
    };
    
    class Mode1993 : public VerbModeBase
    {
    public:
        Mode1993(double sampleRate);
        ~Mode1993() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1993"; }
    };
    
    class Mode1994 : public VerbModeBase
    {
    public:
        Mode1994(double sampleRate);
        ~Mode1994() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1994"; }
    };
    
    class Mode1995 : public VerbModeBase
    {
    public:
        Mode1995(double sampleRate);
        ~Mode1995() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "1995"; }
    };
    
    // ============================================================================
    // NOW Modes
    // ============================================================================
    
    class ModeNOW1 : public VerbModeBase
    {
    public:
        ModeNOW1(double sampleRate);
        ~ModeNOW1() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "NOW1"; }
    };
    
    class ModeNOW2 : public VerbModeBase
    {
    public:
        ModeNOW2(double sampleRate);
        ~ModeNOW2() override;
        
        void configureFDN(FDNReverb* fdn) override;
        juce::String getName() const override { return "NOW2"; }
    };
    
    // ============================================================================
    // Mode Factory
    // ============================================================================
    
    /**
     * Create a verb mode processor based on mode enum.
     */
    VerbModeBase* createVerbMode(VerbMode mode, double sampleRate);
    
    /**
     * Create a verb mode processor based on mode name.
     */
    VerbModeBase* createVerbMode(const juce::String& modeName, double sampleRate);
}
