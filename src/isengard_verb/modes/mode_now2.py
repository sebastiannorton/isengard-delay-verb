"""
Mode NOW2 - Modern Algorithm 2

Modern reverb algorithm with experimental characteristics.

Characteristics:
- Dense, immersive sound
- Complex modulation
- Unique spatial characteristics
- Experimental routing

Category: Modern
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class ModeNOW2(VerbModeBase):
    """
    Modern Algorithm 2 (NOW).
    
    An experimental modern reverb algorithm with dense, immersive sound,
    complex modulation, and unique spatial characteristics.
    """
    
    name = "NOW2"
    year = 2020
    description = "Modern Algorithm 2 - Dense, immersive reverb with complex modulation and unique spatial characteristics"
    category = "Modern"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.75,
        'size': 0.9,
        'damping': 0.25,
        'damping_freq': 16000.0,
        'diffusion': 0.9,
        'mod_rate': 0.15,
        'mod_depth': 0.25,
        'pre_delay': 120.0,
        'early_level': 0.25,
        'width': 0.95,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Modern Algorithm 2-specific parameters."""
        # Experimental routing with very long delays
        self.fdn.comb_delays_ms = [1600.0, 2000.0, 2400.0, 2800.0]
        self.fdn.comb_feedbacks = [0.87, 0.89, 0.91, 0.93]
        self.fdn.allpass_delays_ms = [10.0, 12.0]
        self.fdn.allpass_feedbacks = [0.77, 0.82]
        
        self._update_fdn()
        
        # Experimental early reflection pattern
        self.early_reflections.taps = [
            (10.0, 0.5, 0.3),
            (30.0, 0.45, 0.35),
            (60.0, 0.4, 0.4),
            (100.0, 0.35, 0.45),
            (150.0, 0.3, 0.5),
            (210.0, 0.25, 0.55),
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
    print("Testing ModeNOW2 (Modern Algorithm 2)...")
    mode = ModeNOW2(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('ModeNOW2 test completed successfully!')
