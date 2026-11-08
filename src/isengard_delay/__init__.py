"""
Isengard Delay - Delay/Echo Processor

This package provides a comprehensive delay/echo processor with 7 modes
and 5 styles inspired by ValhallaDelay.

Main Components:
- DelayProcessor: Unified delay processor
- modes: 7 delay modes (Tape, HiFi, BBD, Digital, Ghost, Pitch, RevPitch)
- styles: 5 delay styles (Single, Dual, Ratio, PingPong, Quad)

Usage:
    from isengard_delay import DelayProcessor
    
    processor = DelayProcessor(sample_rate=44100)
    processor.set_mode('tape')
    processor.set_style('pingpong')
    processor.set_parameters({'delay_time_ms': 500, 'feedback': 0.5, 'mix': 0.5})
    
    output = processor.process_block(input_audio)
"""

from .processor import DelayProcessor
from .modes import TapeMode, HiFiMode, BBDMode, DigitalMode, GhostMode, PitchMode, RevPitchMode
from .styles import SingleStyle, DualStyle, RatioStyle, PingPongStyle, QuadStyle

__all__ = [
    'DelayProcessor',
    'TapeMode', 'HiFiMode', 'BBDMode', 'DigitalMode', 'GhostMode', 'PitchMode', 'RevPitchMode',
    'SingleStyle', 'DualStyle', 'RatioStyle', 'PingPongStyle', 'QuadStyle',
]

__version__ = "0.1.0"
