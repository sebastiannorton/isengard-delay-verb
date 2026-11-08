"""
Mode 1990 - Lexicon PCM70

Based on the Lexicon PCM70 (1990).

Characteristics:
- Classic effects processor with reverb
- Versatile algorithms
- Good for both reverb and effects
- Characteristic Lexicon sound

Category: Hall
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1990(VerbModeBase):
    """
    Lexicon PCM70 (1990).
    
    The Lexicon PCM70 was a classic effects processor that included
    high-quality reverb algorithms with the characteristic Lexicon sound.
    """
    
    name = "1990"
    year = 1990
    description = "Lexicon PCM70 - Classic effects processor with versatile reverb algorithms"
    category = "Hall"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.65,
        'size': 0.72,
        'damping': 0.45,
        'damping_freq': 11000.0,
        'diffusion': 0.76,
        'mod_rate': 0.35,
        'mod_depth': 0.13,
        'pre_delay': 75.0,
        'early_level': 0.45,
        'width': 0.75,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Lexicon PCM70-specific parameters."""
        self.fdn.comb_delays_ms = [1100.0, 1300.0, 1500.0, 1700.0]
        self.fdn.comb_feedbacks = [0.81, 0.83, 0.85, 0.87]
        self.fdn.allpass_delays_ms = [6.5, 8.5]
        self.fdn.allpass_feedbacks = [0.71, 0.76]
        
        self._update_fdn()
        
        self.early_reflections.taps = [
            (25.0, 0.58, 0.45),
            (55.0, 0.52, 0.5),
            (90.0, 0.48, 0.55),
            (130.0, 0.42, 0.6),
        ]
    
    def get_name(self) -> str:
        return self.name
    
    def get_year(self) -> int:
        return self.year
    
    def get_description(self) -> str:
        return self.description
    
    def get_category(self) -> str:
        return self.category


# Test
if __name__ == "__main__":
    print("Testing Mode1990 (Lexicon PCM70)...")
    mode = Mode1990(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1990 test completed successfully!')
