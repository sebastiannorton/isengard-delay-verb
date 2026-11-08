"""
Mode 1975 - Eventide SP2016

Based on the Eventide SP2016 (1975).

Characteristics:
- Early digital effects processor
- Versatile reverb algorithms
- Characteristic early reflections
- Flexible parameter control

Category: Digital
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1975(VerbModeBase):
    """
    Eventide SP2016 (1975).
    
    The SP2016 was a versatile digital effects processor with
    various reverb algorithms and flexible parameter control.
    """
    
    name = "1975"
    year = 1975
    description = "Eventide SP2016 - Versatile digital reverb with flexible control"
    category = "Digital"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.5,
        'size': 0.6,
        'damping': 0.5,
        'damping_freq': 10000.0,
        'diffusion': 0.6,
        'mod_rate': 0.4,
        'mod_depth': 0.12,
        'pre_delay': 55.0,
        'early_level': 0.5,
        'width': 0.6,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize SP2016-specific parameters."""
        self.fdn.comb_delays_ms = [900.0, 1100.0, 1300.0, 1500.0]
        self.fdn.comb_feedbacks = [0.78, 0.80, 0.82, 0.84]
        self.fdn.allpass_delays_ms = [5.0, 7.0]
        self.fdn.allpass_feedbacks = [0.7, 0.72]
        
        self._update_fdn()
        
        self.early_reflections.taps = [
            (25.0, 0.6, 0.5),
            (50.0, 0.5, 0.6),
            (75.0, 0.4, 0.5),
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
    print("Testing Mode1975 (Eventide SP2016)...")
    mode = Mode1975(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1975 test completed successfully!')
