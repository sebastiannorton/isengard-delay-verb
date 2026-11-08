"""
Mode 1986 - Yamaha Rev5

Based on the Yamaha Rev5 (1986).

Characteristics:
- Popular Yamaha digital reverb
- Bright, clear sound
- Good for vocals and instruments
- Characteristic Yamaha high-end clarity

Category: Room
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1986(VerbModeBase):
    """
    Yamaha Rev5 (1986).
    
    The Yamaha Rev5 was a popular digital reverb known for
    its bright, clear sound and good vocal performance.
    """
    
    name = "1986"
    year = 1986
    description = "Yamaha Rev5 - Bright, clear digital reverb with characteristic Yamaha high-end clarity"
    category = "Room"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.6,
        'size': 0.65,
        'damping': 0.4,
        'damping_freq': 12000.0,
        'diffusion': 0.7,
        'mod_rate': 0.4,
        'mod_depth': 0.1,
        'pre_delay': 50.0,
        'early_level': 0.55,
        'width': 0.7,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Yamaha Rev5-specific parameters."""
        self.fdn.comb_delays_ms = [800.0, 1000.0, 1200.0, 1400.0]
        self.fdn.comb_feedbacks = [0.79, 0.81, 0.83, 0.85]
        self.fdn.allpass_delays_ms = [5.0, 7.0]
        self.fdn.allpass_feedbacks = [0.68, 0.73]
        
        self._update_fdn()
        
        self.early_reflections.taps = [
            (15.0, 0.6, 0.45),
            (35.0, 0.55, 0.5),
            (60.0, 0.5, 0.55),
            (90.0, 0.45, 0.6),
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
    print("Testing Mode1986 (Yamaha Rev5)...")
    mode = Mode1986(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1986 test completed successfully!')
