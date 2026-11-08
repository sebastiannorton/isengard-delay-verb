# Known Unknowns

**Project:** Isengard Delay & Isengard Verb  
**Phase:** B - Reference Investigation  
**Status:** INITIAL LIST

---

## 1. Critical Unknowns (Block Progress)

### KU001 - Plugin Binary Access

**Question:** How can we access the full Valhalla plugin binaries for analysis?

**Impact:** HIGH - Blocks Phase B (Reference Investigation)

**Current Status:**
- Located binaries in Google Drive (IDs: `1kszyDJ4b8QMCteQxhf8UOmSa5qVFYWWm`, `1H9tdz-6edzVeyNwYgPWnwjFC6wmnJdh0`)
- Size: 5.6 MB and 2.7 MB
- Google Drive MCP has 2MB size limit for downloads
- Network requests (wget, curl) are blocked in sandbox

**Potential Solutions:**
1. **Alternative Download Method:** Use host system to download and transfer files
2. **Partial Analysis:** Download only resource files (smaller) for string analysis
3. **Skip Binary Analysis:** Focus on documentation-based reconstruction
4. **MCP Enhancement:** Request larger payload support for Google Drive MCP

**Workaround:** Proceed with documentation analysis and implement based on public knowledge

---

### KU002 - Native Analysis Provider

**Question:** How can we configure a native analysis provider for REA?

**Impact:** HIGH - Limits Phase B investigation depth

**Current Status:**
- REA installed and functional (v6.8.0)
- No native analysis providers configured (Hopper, Ghidra, IDA, JADX, Kuna)
- Network restrictions prevent downloading Ghidra
- Ghidra not available via apt

**Potential Solutions:**
1. **Install Ghidra Locally:** Download on host system and copy to sandbox
2. **Use Existing Tools:** Use binutils (objdump, readelf) for basic analysis
3. **REA Bridge:** Configure REA to use binutils for basic inspection
4. **Alternative Providers:** Check if any other tools are available

**Workaround:** Use REA's built-in analysis capabilities with available tools

---

## 2. Major Unknowns (Affect Architecture)

### KU003 - Exact Delay-Line Implementation

**Question:** What is the exact delay-line implementation in ValhallaDelay?

**Impact:** MEDIUM - Affects DSP accuracy

**Current Status:**
- Hypothesis: Multi-tap delay line with feedback matrix
- No binary evidence to confirm
- Multiple modes suggest different topologies

**Evidence Needed:**
- Binary analysis of delay-line code
- Impulse response testing
- Parameter sweep analysis

**Workaround:** Implement standard delay-line structures and tune by ear

---

### KU004 - Exact Reverb Network Architecture

**Question:** What is the exact reverb network architecture in ValhallaVintageVerb?

**Impact:** MEDIUM - Affects DSP accuracy

**Current Status:**
- Hypothesis: Feedback Delay Network (FDN) with allpass filters
- 22 modes suggest different configurations
- No binary evidence to confirm

**Evidence Needed:**
- Binary analysis of reverb network code
- Impulse response analysis
- Decay curve measurements

**Workaround:** Implement standard FDN and allpass structures, tune by ear

---

### KU005 - Parameter Internal Mappings

**Question:** What are the exact internal value ranges and mappings for each parameter?

**Impact:** MEDIUM - Affects parameter feel and usability

**Current Status:**
- Documentation provides parameter names and general behavior
- No information on internal value ranges
- No information on mapping functions (linear, log, etc.)

**Evidence Needed:**
- Binary analysis of parameter handling code
- Black-box testing with known inputs
- Preset analysis (if available)

**Workaround:** Use standard audio DSP conventions for parameter mappings

---

## 3. Minor Unknowns (Affect Details)

### KU006 - Mode-Specific Parameter Availability

**Question:** Which parameters are available in which modes?

**Impact:** LOW - Affects UI/UX design

**Current Status:**
- Documentation mentions modes but not parameter availability
- Some parameters likely mode-specific

**Evidence Needed:**
- Plugin GUI inspection
- Binary analysis of mode switching code
- Documentation deep-dive

**Workaround:** Make all parameters available in all modes, with mode-specific defaults

---

### KU007 - Exact Modulation Implementation

**Question:** How is modulation implemented in both plugins?

**Impact:** LOW - Affects sound character

**Current Status:**
- Parameters: Mod Rate, Mod Depth
- Hypothesis: LFO-based delay time or filter modulation
- No details on LFO shape, phase, or exact targets

**Evidence Needed:**
- Binary analysis of modulation code
- Audio testing with modulation parameters
- Spectrogram analysis

**Workaround:** Implement sine LFO with standard targets (delay time, filter cutoff)

---

### KU008 - Diffusion Network Details

**Question:** What is the exact structure of the diffusion network in ValhallaDelay?

**Impact:** LOW - Affects echo density characteristics

**Current Status:**
- Parameters: Diffusion, Diffusion Size, Diffusion Amount
- Hypothesis: Allpass filters in series/parallel
- No details on exact structure

**Evidence Needed:**
- Binary analysis of diffusion code
- Audio testing with diffusion parameters
- Impulse response analysis

**Workaround:** Implement standard allpass diffusion network with configurable size

---

### KU009 - Pitch/Frequency Shift Implementation

**Question:** How are pitch and frequency shifting implemented?

**Impact:** LOW - Affects sound quality

**Current Status:**
- Parameters: Pitch Shift, Pitch Detune, Frequency Shift, Frequency Detune
- Hypothesis: Time-domain (PSOLA) or frequency-domain (phase vocoder)
- No details on exact implementation

**Evidence Needed:**
- Binary analysis of pitch shift code
- Audio testing with pitch parameters
- Artifact analysis

**Workaround:** Implement phase vocoder for high quality, PSOLA for efficiency

---

### KU010 - Age and Drive Implementation

**Question:** How are Age and Drive parameters implemented?

**Impact:** LOW - Affects tone shaping

**Current Status:**
- Age: Likely bandwidth reduction and degradation
- Drive: Likely saturation/nonlinear distortion
- No details on exact algorithms

**Evidence Needed:**
- Binary analysis of tone shaping code
- Audio testing with Age and Drive parameters
- Frequency response analysis

**Workaround:** Implement standard saturation and filtering algorithms

---

## 4. Documentation Unknowns

### KU011 - Complete Mode List

**Question:** What are all 22 modes in ValhallaVintageVerb?

**Impact:** LOW - Affects preset design

**Current Status:**
- Documentation mentions 22 modes and 3 colors
- No complete list available

**Evidence Needed:**
- Plugin GUI inspection
- Documentation deep-dive
- Binary string analysis

**Workaround:** Implement representative modes from known categories

---

### KU012 - Version-Specific Features

**Question:** What features are available in the installed versions (2018-2019)?

**Impact:** LOW - Affects feature completeness

**Current Status:**
- ValhallaDelay: Version from 2019-10-21
- ValhallaVintageVerb: Version from 2018-07-21
- Current versions may have additional features

**Evidence Needed:**
- Version history analysis
- Binary comparison with newer versions
- Documentation comparison

**Workaround:** Implement based on installed version features as documented

---

## 5. Technical Unknowns

### KU013 - Sample Rate Handling

**Question:** How do the plugins handle different sample rates?

**Impact:** LOW - Affects compatibility

**Current Status:**
- macOS AU plugins support multiple sample rates
- No details on internal handling

**Evidence Needed:**
- Binary analysis of sample rate handling code
- Testing at different sample rates

**Workaround:** Implement sample-rate-independent algorithms

---

### KU014 - CPU Optimization Techniques

**Question:** What CPU optimization techniques are used?

**Impact:** LOW - Affects performance

**Current Status:**
- Valhalla plugins are known for efficiency
- No details on specific optimizations

**Evidence Needed:**
- Binary analysis of hot code paths
- Performance profiling

**Workaround:** Use standard optimization techniques (SIMD, block processing, etc.)

---

### KU015 - Denormal Handling

**Question:** How do the plugins handle denormal numbers?

**Impact:** LOW - Affects stability

**Current Status:**
- No information available

**Evidence Needed:**
- Binary analysis of denormal handling code
- Testing with denormal-prone signals

**Workaround:** Implement standard denormal handling (flush to zero, add noise)

---

## 6. Resolution Strategy

### Priority Order

1. **KU001** - Plugin Binary Access (HIGH)
   - Find alternative download method
   - Proceed without binary analysis if necessary

2. **KU002** - Native Analysis Provider (HIGH)
   - Install Ghidra or use binutils
   - Configure REA with available tools

3. **KU003, KU004** - DSP Architecture (MEDIUM)
   - Use REA for binary analysis (when available)
   - Implement based on documentation and standard techniques

4. **KU005** - Parameter Mappings (MEDIUM)
   - Use standard audio DSP conventions
   - Tune by ear and measurement

5. **KU006-KU015** - Details (LOW)
   - Implement reasonable defaults
   - Refine during Phase G (Comparison and Refinement)

---

## 7. Acceptance Criteria

For each unknown, we must either:
1. **Resolve:** Find definitive answer through investigation
2. **Work Around:** Implement reasonable alternative with documentation
3. **Accept:** Document as known deviation from reference

---

## 8. Progress Tracking

| ID | Status | Resolution | Workaround |
|----|--------|------------|------------|
| KU001 | Open | | Partial analysis possible |
| KU002 | Open | | Use binutils |
| KU003 | Open | | Standard implementation |
| KU004 | Open | | Standard implementation |
| KU005 | Open | | Standard mappings |
| KU006 | Open | | All parameters available |
| KU007 | Open | | Standard modulation |
| KU008 | Open | | Standard diffusion |
| KU009 | Open | | Standard pitch shift |
| KU010 | Open | | Standard saturation |
| KU011 | Open | | Representative modes |
| KU012 | Open | | Installed version features |
| KU013 | Open | | Sample-rate independent |
| KU014 | Open | | Standard optimizations |
| KU015 | Open | | Standard denormal handling |

---

**Last Updated:** 2026-11-07  
**Author:** Vibe Code (Mistral AI)
