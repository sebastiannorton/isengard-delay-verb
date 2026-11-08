"""
Mode 1985 - Lexicon 300

Based on the Lexicon 300 (1985).

Characteristics:
- Mid-range Lexicon reverb
- Versatile algorithms
- Good balance of quality and affordability
- Clear, detailed sound

Category: Hall
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1985(VerbModeBase):
    """
    Lexicon 300 (1985).
    
    The Lexicon 300 was a mid-range digital reverb that offered
    a good balance of quality and affordability with versatile algorithms.
    """
    
    name = "1985"
    year = 1985
    description = "Lexicon 300 - Versatile digital reverb with clear, detailed sound"
    category = "Hall"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.65,
        'size': 0.7,
        'damping': 0.45,
        'damping_freq': 11000.0,
        'diffusion': 0.75,
        'mod_rate': 0.35,
        'mod_depth': 0.14,
        'pre_delay': 70.0,
        'early_level': 0.45,
        'width': 0.75,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Lexicon 300-specific parameters."""
        self.fdn.comb_delays_ms = [1000.0, 1250.0, 1500.0, 1750.0]
        self.fdn.comb_feedbacks = [0.82, 0.84, 0.86, 0.88]
        self.fdn.allpass_delays_ms = [7.0, 9.0]
        self.fdn.allpass_feedbacks = [0.72, 0.78]
        
        self._update_fdn()
        
        self.early_reflections.taps = [
            (25.0, 0.55, 0.5),
            (55.0, 0.5, 0.55),
            (85.0, 0.45, 0.6),
            (120.0, 0.4, 0.65),
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
    print("Testing Mode1985 (Lexicon 300)...")
    mode = Mode1985(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1985 test completed successfully!')
