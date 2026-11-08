"""
Mode 1993 - TC Electronic M3000

Based on the TC Electronic M3000 (1993).

Characteristics:
- High-end TC Electronic reverb
- Pristine sound quality
- Advanced algorithms
- Professional studio standard

Category: Hall
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1993(VerbModeBase):
    """
    TC Electronic M3000 (1993).
    
    The TC Electronic M3000 was a high-end digital reverb known for
    its pristine sound quality and advanced algorithms.
    """
    
    name = "1993"
    year = 1993
    description = "TC Electronic M3000 - High-end digital reverb with pristine sound quality"
    category = "Hall"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.7,
        'size': 0.8,
        'damping': 0.35,
        'damping_freq': 13500.0,
        'diffusion': 0.82,
        'mod_rate': 0.28,
        'mod_depth': 0.16,
        'pre_delay': 90.0,
        'early_level': 0.38,
        'width': 0.82,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize TC Electronic M3000-specific parameters."""
        self.fdn.comb_delays_ms = [1400.0, 1650.0, 1900.0, 2150.0]
        self.fdn.comb_feedbacks = [0.85, 0.87, 0.89, 0.91]
        self.fdn.allpass_delays_ms = [8.0, 10.0]
        self.fdn.allpass_feedbacks = [0.74, 0.79]
        
        self._update_fdn()
        
        self.early_reflections.taps = [
            (20.0, 0.58, 0.4),
            (50.0, 0.52, 0.45),
            (85.0, 0.48, 0.5),
            (130.0, 0.42, 0.55),
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
    print("Testing Mode1993 (TC Electronic M3000)...")
    mode = Mode1993(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1993 test completed successfully!')
