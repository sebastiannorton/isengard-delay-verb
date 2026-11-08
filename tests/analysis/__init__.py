# Isengard Analysis Tools
# Signal analysis for Phase C: Experimental Validation

"""
Signal analysis tools for Isengard Delay & Isengard Verb testing.

This module provides analysis tools for:
- FFT and spectral analysis
- Impulse response analysis
- Decay curve analysis
- Stereo correlation analysis
- Comparison metrics

All tools are:
- Sample-rate aware
- Well-documented
- Deterministic where applicable
- Optimized for audio analysis
"""

from .fft import FFTAnalyzer
from .impulse import ImpulseAnalyzer
from .decay import DecayAnalyzer
from .stereo import StereoAnalyzer
from .metrics import ComparisonMetrics

__all__ = [
    'FFTAnalyzer',
    'ImpulseAnalyzer',
    'DecayAnalyzer',
    'StereoAnalyzer',
    'ComparisonMetrics',
]

__version__ = '1.0.0'
__description__ = 'Signal analysis tools for Isengard plugin testing'

# Convenience function to create all analyzers
def create_all_analyzers(sample_rate=44100):
    """
    Create all analyzer instances with the same sample rate.
    
    Args:
        sample_rate: Sample rate in Hz
        
    Returns:
        dict: Dictionary containing all analyzer instances
    """
    return {
        'fft': FFTAnalyzer(sample_rate),
        'impulse': ImpulseAnalyzer(sample_rate),
        'decay': DecayAnalyzer(sample_rate),
        'stereo': StereoAnalyzer(),
        'metrics': ComparisonMetrics(),
    }
