# Isengard Delay & Isengard Verb

## Overview

Two independent, high-quality macOS audio plugins inspired by ValhallaDelay and ValhallaVintageVerb.

- **Isengard Delay** - Comprehensive delay/echo processor with 7 modes and 5 styles
- **Isengard Verb** - Algorithmic reverb processor with 22 modes and 3 color settings

Both plugins ship as native Audio Unit (AU) and VST3 plugins for macOS, supporting Apple Silicon and Intel architectures.

## Project Structure

```
.
├── docs/                    # Documentation
├── research/               # Research and evidence
├── src/                    # Python DSP implementations
│   ├── isengard_delay/     # Delay processor
│   ├── isengard_verb/      # Reverb processor
│   └── isengard_shared/    # Shared components
├── tests/                  # Test framework
├── juce/                   # JUCE C++ plugin code
└── *.md                   # Project documentation
```

## Quick Start

See `juce/README.md` for build instructions.

## License

This project is proprietary. Do not redistribute without permission.
