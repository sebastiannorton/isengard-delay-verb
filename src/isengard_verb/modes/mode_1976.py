"""
Mode 1976 - EMT 250 Electronic Reverb

Based on the EMT 250 (1976).

Characteristics:
- Electronic reverb (not plate)
- Long, smooth decay
- Characteristic "hall" sound
- Rich early reflections

Category: Hall
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1976(VerbModeBase):
    """
    EMT 250 Electronic Reverb (1976).
    
    The EMT 250 was an electronic reverb unit that used a
    recirculating delay line to create a hall-like sound.
    """
    
    name = "1976"
    year = 1976
    description = "EMT 250 - Electronic reverb with long, smooth hall decay"
    category = "Hall"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.7,        # Long decay for hall
        'size': 0.8,         # Large hall
        'damping': 0.5,
        'damping_freq': 9000.0,
        'diffusion': 0.8,    # High diffusion for hall
        'mod_rate': 0.2,
        'mod_depth': 0.1,
        'pre_delay': 70.0,
        'early_level': 0.5,
        'width': 0.7,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize EMT 250-specific parameters."""
        self.fdn.comb_delays_ms = [1300.0, 1500.0, 1700.0, 1900.0]
        self.fdn.comb_feedbacks = [0.83, 0.85, 0.87, 0.89]
        self.fdn.allpass_delays_ms = [7.0, 9.0]
        self.fdn.allpass_feedbacks = [0.75, 0.80]
        
        self._update_fdn()
        
        # EMT 250 had rich early reflections
        self.early_reflections.taps = [
            (20.0, 0.6, 0.5),
            (40.0, 0.5, 0.6),
            (60.0, 0.5, 0.5),
            (80.0, 0.4, 0.6),
            (100.0, 0.4, 0.5),
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
    print("Testing Mode1976 (EMT 250)...")
    mode = Mode1976(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1976 test completed successfully!')
