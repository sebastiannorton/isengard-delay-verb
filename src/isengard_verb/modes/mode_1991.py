"""
Mode 1991 - Yamaha Rev7

Based on the Yamaha Rev7 (1991).

Characteristics:
- Advanced Yamaha digital reverb
- Clean, detailed sound
- Good for modern productions
- Versatile algorithms

Category: Hall
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1991(VerbModeBase):
    """
    Yamaha Rev7 (1991).
    
    The Yamaha Rev7 was an advanced digital reverb known for
    its clean, detailed sound and versatile algorithms.
    """
    
    name = "1991"
    year = 1991
    description = "Yamaha Rev7 - Advanced digital reverb with clean, detailed sound"
    category = "Hall"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.62,
        'size': 0.7,
        'damping': 0.42,
        'damping_freq': 12500.0,
        'diffusion': 0.74,
        'mod_rate': 0.4,
        'mod_depth': 0.12,
        'pre_delay': 60.0,
        'early_level': 0.5,
        'width': 0.72,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Yamaha Rev7-specific parameters."""
        self.fdn.comb_delays_ms = [900.0, 1100.0, 1300.0, 1500.0]
        self.fdn.comb_feedbacks = [0.80, 0.82, 0.84, 0.86]
        self.fdn.allpass_delays_ms = [6.0, 8.0]
        self.fdn.allpass_feedbacks = [0.70, 0.75]
        
        self._update_fdn()
        
        self.early_reflections.taps = [
            (20.0, 0.6, 0.4),
            (45.0, 0.55, 0.45),
            (75.0, 0.5, 0.5),
            (110.0, 0.45, 0.55),
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
    print("Testing Mode1991 (Yamaha Rev7)...")
    mode = Mode1991(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1991 test completed successfully!')
