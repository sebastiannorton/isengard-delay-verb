"""
Mode 1979 - AMS RMX16 Variant

Based on a variant of the AMS RMX16 (1979).

Characteristics:
- Digital reverb with unique characteristics
- Slightly different from 1974 model
- Balanced decay and diffusion

Category: Digital
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1979(VerbModeBase):
    """
    AMS RMX16 Variant (1979).
    """
    
    name = "1979"
    year = 1979
    description = "AMS RMX16 Variant - Digital reverb with balanced characteristics"
    category = "Digital"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.5,
        'size': 0.6,
        'damping': 0.5,
        'damping_freq': 11000.0,
        'diffusion': 0.6,
        'mod_rate': 0.5,
        'mod_depth': 0.12,
        'pre_delay': 55.0,
        'early_level': 0.5,
        'width': 0.6,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize 1979-specific parameters."""
        self.fdn.comb_delays_ms = [900.0, 1100.0, 1300.0, 1500.0]
        self.fdn.comb_feedbacks = [0.77, 0.79, 0.81, 0.83]
        self.fdn.allpass_delays_ms = [5.0, 7.0]
        self.fdn.allpass_feedbacks = [0.68, 0.72]
        
        self._update_fdn()
        
        self.early_reflections.taps = [
            (22.0, 0.6, 0.5),
            (44.0, 0.5, 0.6),
            (66.0, 0.4, 0.5),
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
    print("Testing Mode1979...")
    mode = Mode1979(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1979 test completed successfully!')
