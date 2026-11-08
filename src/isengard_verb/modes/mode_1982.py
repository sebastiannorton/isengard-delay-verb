"""
Mode 1982 - Sony DRP-F300

Based on the Sony DRP-F300 (1982).

Characteristics:
- Early digital reverb from Sony
- Warm, natural sound
- Good for vocal applications
- Balanced frequency response

Category: Hall
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1982(VerbModeBase):
    """
    Sony DRP-F300 (1982).
    
    The Sony DRP-F300 was an early digital reverb known for
    its warm, natural sound and good vocal performance.
    """
    
    name = "1982"
    year = 1982
    description = "Sony DRP-F300 - Warm, natural digital reverb with balanced frequency response"
    category = "Hall"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.6,
        'size': 0.65,
        'damping': 0.55,
        'damping_freq': 9000.0,
        'diffusion': 0.7,
        'mod_rate': 0.3,
        'mod_depth': 0.14,
        'pre_delay': 60.0,
        'early_level': 0.5,
        'width': 0.65,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Sony DRP-F300-specific parameters."""
        self.fdn.comb_delays_ms = [900.0, 1100.0, 1300.0, 1500.0]
        self.fdn.comb_feedbacks = [0.80, 0.82, 0.84, 0.86]
        self.fdn.allpass_delays_ms = [6.0, 8.0]
        self.fdn.allpass_feedbacks = [0.7, 0.75]
        
        self._update_fdn()
        
        self.early_reflections.taps = [
            (25.0, 0.55, 0.5),
            (50.0, 0.5, 0.55),
            (80.0, 0.45, 0.6),
            (110.0, 0.4, 0.6),
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
    print("Testing Mode1982 (Sony DRP-F300)...")
    mode = Mode1982(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1982 test completed successfully!')
