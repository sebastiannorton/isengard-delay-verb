"""
Isengard Verb - Algorithmic Reverb Processor

This package provides a comprehensive algorithmic reverb processor
with 22 modes inspired by classic digital reverb hardware.

Main Components:
- VerbProcessor: Unified reverb processor
- modes: 22 reverb modes (1972-1995, NOW1, NOW2)
- dsp: DSP components (FDN, early reflections, modulation, color)

Usage:
    from isengard_verb import VerbProcessor
    
    processor = VerbProcessor(sample_rate=44100)
    processor.set_mode('1978')  # Lexicon 224
    processor.set_color('1980s')
    processor.set_parameters({'decay': 0.7, 'mix': 0.5})
    
    output = processor.process_block(input_audio)
"""

from .processor import VerbProcessor
from .modes import get_mode, list_modes, VerbModeBase
from .dsp import FDNReverb, EarlyReflections, ModulationMatrix, LFO, ColorSystem

__all__ = [
    'VerbProcessor',
    'get_mode', 'list_modes', 'VerbModeBase',
    'FDNReverb', 'EarlyReflections', 'ModulationMatrix', 'LFO', 'ColorSystem',
]

__version__ = "0.1.0"
