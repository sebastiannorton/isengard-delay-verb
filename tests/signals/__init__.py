# Isengard Test Signals
# Signal generators for Phase C: Experimental Validation

"""
Test signal generation framework for Isengard Delay & Isengard Verb.

This module provides deterministic test signal generators for:
- Impulse signals (for impulse response measurement)
- Noise signals (white, pink) (for frequency response analysis)
- Sine waves (for frequency accuracy testing)
- Frequency sweeps (for frequency response analysis)
- Tone bursts (for transient response analysis)

All generators are:
- Deterministic (reproducible with seed)
- Sample-rate independent
- Stereo-capable
- Well-documented
"""

from .impulse import ImpulseGenerator
from .noise import NoiseGenerator
from .sine import SineGenerator
from .sweep import SweepGenerator
from .burst import BurstGenerator

__all__ = [
    'ImpulseGenerator',
    'NoiseGenerator',
    'SineGenerator',
    'SweepGenerator',
    'BurstGenerator',
]

__version__ = '1.0.0'
__description__ = 'Test signal generators for Isengard plugin testing'

# Convenience function to create all generators
def create_all_generators(sample_rate=44100, length_samples=44100):
    """
    Create all signal generators with the same sample rate and length.
    
    Args:
        sample_rate: Sample rate in Hz
        length_samples: Length of generated signals in samples
        
    Returns:
        dict: Dictionary containing all generator instances
    """
    return {
        'impulse': ImpulseGenerator(sample_rate, length_samples),
        'noise': NoiseGenerator(sample_rate, length_samples),
        'sine': SineGenerator(sample_rate, length_samples),
        'sweep': SweepGenerator(sample_rate, length_samples),
        'burst': BurstGenerator(sample_rate, length_samples),
    }

__version__ = '1.0.0'
