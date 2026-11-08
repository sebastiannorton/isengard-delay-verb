# Isengard Delay & Isengard Verb

## Evidence-driven DSP reconstruction using REA

Two independent, high-quality macOS audio plugins inspired by ValhallaDelay and ValhallaVintageVerb.

- **Isengard Delay** — Comprehensive delay/echo processor with 7 modes and 5 styles
- **Isengard Verb** — Comprehensive algorithmic reverb processor with 22 modes and 3 color settings

Both plugins ship as native Audio Unit (AU) and VST3 plugins for macOS with Apple Silicon and Intel support.

**✅ All project files now available in this GitHub repository!**

## Project Structure

```
isengard-project/
├── research/                    # Research documentation (8 files)
│   ├── valhalla-delay-documentation.md  # Comprehensive ValhallaDelay analysis
│   ├── valhalla-vintageverb-documentation.md  # Comprehensive VintageVerb analysis
│   ├── evidence-ledger.md        # 99+ evidence entries tracked
│   ├── dsp-architecture.md       # DSP architecture findings
│   ├── parameter-mappings.md     # Parameter behavior documentation
│   ├── known-unknowns.md         # Resolved uncertainties
│   ├── rea-investigation.md      # REA tool investigation
│   └── living-compass-summary.md # Design principles
├── docs/                        # Development documentation (11 files)
│   ├── isengard-delay-dsp-spec-v1.md  # Delay DSP specification
│   ├── isengard-verb-dsp-spec-v1.md   # Verb DSP specification
│   └── SESSION-*.md              # Session summaries
├── src/                         # Python DSP prototypes (68 files)
│   ├── isengard_shared/          # Shared DSP components
│   ├── isengard_delay/           # Delay processor + 7 modes + 5 styles
│   └── isengard_verb/            # Verb processor + 22 modes + 3 colors
├── tests/                       # Test suite (114 files)
│   ├── reference_rendering/      # Rendering framework + 114 configs
│   ├── signals/                  # Test signal generators
│   ├── analysis/                 # Analysis tools
│   └── parameter_sweeps/         # Parameter sweep framework
├── juce/                        # JUCE plugin implementation (14 files)
│   ├── CMakeLists.txt            # CMake build configuration
│   ├── Shared/                   # Shared C++ DSP headers
│   ├── IsengardDelay/           # AU/VST3 delay plugin
│   └── IsengardVerb/             # AU/VST3 verb plugin
├── SESSION-*.md                 # Session progress reports
└── README.md                    # This file
```

## Phases

1. **Phase A** - Environment Assessment ✅ COMPLETE
2. **Phase B** - Reference Investigation ✅ COMPLETE
3. **Phase C** - Experimental Validation ✅ COMPLETE
4. **Phase D** - DSP Architecture ✅ COMPLETE
5. **Phase E** - Interface Design ⏳ PARTIAL
6. **Phase F** - Implementation ⏳ PARTIAL (JUCE structure created)
7. **Phase G** - Comparison and Refinement ⏳ PENDING
8. **Phase H** - Delivery ⏳ PENDING

## Status

✅ **COMPLETED:**
- Phase A: Environment Assessment
- Phase B: Reference Investigation (43 verified evidence entries)
- Phase C: Experimental Validation (114 test configs, full test framework)
- Phase D: DSP Architecture (7 delay modes, 5 styles, 22 verb modes, 3 colors)

⏳ **IN PROGRESS:**
- Phase E: Interface Design (Living Compass principles documented)
- Phase F: Implementation (Python prototypes complete, JUCE C++ structure created)

⏳ **PENDING:**
- Phase G: Comparison and Refinement
- Phase H: Delivery (AU/VST3 builds)

## GitHub Repository

📁 **All 253 files are now in GitHub:**
- Repository: https://github.com/sebastiannorton/isengard-delay-verb
- Branch: main
- Total files: 253 (252 project files + 1 session summary)
- Last updated: Session 11

## Quick Start

### Clone the Repository
```bash
gh repo clone sebastiannorton/isengard-delay-verb
cd isengard-delay-verb
```

### Set up Python Environment
```bash
# Install dependencies for testing and analysis
pip install numpy scipy soundfile
```

### Build the Plugins (JUCE required)
```bash
# Navigate to JUCE directory
cd juce

# Create build directory
mkdir build && cd build

# Build with CMake
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
```

### Run Tests
```bash
# Run Python test suite
python3 tests/reference_rendering/render.py --config tests/reference_rendering/configs/delay-modes/tape-single-impulse.json
```

### Set up REA for Reverse Engineering
```bash
# Install REA
npm install -g rea

# Configure native analysis providers (Hopper, Ghidra, etc.)
rea doctor
```

## References

- [ValhallaDelay Documentation](https://valhalladsp.com/2019/04/16/valhalladelay-the-controls/)
- [ValhallaVintageVerb Documentation](https://valhalladsp.com/2023/02/10/valhallavintageverb-the-modes/)
- [REA - Reverse Engineer Anything](https://github.com/morluto/rea)
- [Living Compass Design Handbook](https://docs.google.com/document/d/12Eb31fJNuYaK6kQhLsB8p1DmjxQELjOkVGuOyn8jTNo/edit)
