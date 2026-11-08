"""
Mode NOW1 - Modern Algorithm 1

Modern reverb algorithm with contemporary characteristics.

Characteristics:
- Clean, transparent sound
- High density
- Smooth decay
- Advanced modulation

Category: Modern
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class ModeNOW1(VerbModeBase):
    """
    Modern Algorithm 1 (NOW).
    
    A contemporary reverb algorithm with clean, transparent sound,
    high density, and advanced modulation capabilities.
    """
    
    name = "NOW1"
    year = 2020
    description = "Modern Algorithm 1 - Clean, transparent reverb with high density and advanced modulation"
    category = "Modern"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.7,
        'size': 0.85,
        'damping': 0.3,
        'damping_freq': 15000.0,
        'diffusion': 0.85,
        'mod_rate': 0.2,
        'mod_depth': 0.2,
        'pre_delay': 100.0,
        'early_level': 0.3,
        'width': 0.9,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Modern Algorithm 1-specific parameters."""
        # Modern algorithms use longer, more complex delays
        self.fdn.comb_delays_ms = [1500.0, 1800.0, 2100.0, 2400.0]
        self.fdn.comb_feedbacks = [0.86, 0.88, 0.90, 0.92]
        self.fdn.allpass_delays_ms = [9.0, 11.0]
        self.fdn.allpass_feedbacks = [0.76, 0.81]
        
        self._update_fdn()
        
        # Modern algorithms have sophisticated early reflections
        self.early_reflections.taps = [
            (15.0, 0.55, 0.35),
            (35.0, 0.5, 0.4),
            (65.0, 0.45, 0.45),
            (105.0, 0.4, 0.5),
            (155.0, 0.35, 0.55),
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
    print("Testing ModeNOW1 (Modern Algorithm 1)...")
    mode = ModeNOW1(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('ModeNOW1 test completed successfully!')
