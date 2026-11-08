"""
Mode 1981 - Yamaha Rev1

Based on the Yamaha Rev1 (1981).

Characteristics:
- First Yamaha digital reverb
- Bright, clear sound
- Simple but effective algorithms
- Characteristic "Yamaha" tone

Category: Room
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1981(VerbModeBase):
    """
    Yamaha Rev1 (1981).
    
    The Yamaha Rev1 was Yamaha's first digital reverb unit,
    known for its bright, clear sound and straightforward operation.
    """
    
    name = "1981"
    year = 1981
    description = "Yamaha Rev1 - Bright, clear digital reverb with characteristic Yamaha tone"
    category = "Room"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.55,       # Medium decay
        'size': 0.6,         # Medium room
        'damping': 0.5,
        'damping_freq': 10000.0,
        'diffusion': 0.65,   # Moderate diffusion
        'mod_rate': 0.4,
        'mod_depth': 0.1,
        'pre_delay': 50.0,
        'early_level': 0.55, # More early reflections
        'width': 0.6,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Yamaha Rev1-specific parameters."""
        # Rev1 had simpler FDN structure
        self.fdn.comb_delays_ms = [800.0, 1000.0, 1200.0, 1400.0]
        self.fdn.comb_feedbacks = [0.78, 0.80, 0.82, 0.84]
        self.fdn.allpass_delays_ms = [5.0, 7.0]
        self.fdn.allpass_feedbacks = [0.7, 0.7]
        
        self._update_fdn()
        
        # Rev1 had prominent early reflections
        self.early_reflections.taps = [
            (15.0, 0.6, 0.5),
            (30.0, 0.55, 0.55),
            (50.0, 0.5, 0.6),
            (70.0, 0.45, 0.6),
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
    print("Testing Mode1981 (Yamaha Rev1)...")
    mode = Mode1981(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1981 test completed successfully!')
