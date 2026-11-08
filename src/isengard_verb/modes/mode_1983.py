"""
Mode 1983 - AKG ADR68K

Based on the AKG ADR68K (1983).

Characteristics:
- Austrian digital reverb
- Clear, transparent sound
- Good stereo imaging
- Flexible routing

Category: Room
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1983(VerbModeBase):
    """
    AKG ADR68K (1983).
    
    The AKG ADR68K was an Austrian digital reverb known for
    its clear, transparent sound and good stereo imaging.
    """
    
    name = "1983"
    year = 1983
    description = "AKG ADR68K - Clear, transparent digital reverb with good stereo imaging"
    category = "Room"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.58,
        'size': 0.62,
        'damping': 0.48,
        'damping_freq': 11000.0,
        'diffusion': 0.68,
        'mod_rate': 0.38,
        'mod_depth': 0.11,
        'pre_delay': 55.0,
        'early_level': 0.52,
        'width': 0.7,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize AKG ADR68K-specific parameters."""
        self.fdn.comb_delays_ms = [850.0, 1050.0, 1250.0, 1450.0]
        self.fdn.comb_feedbacks = [0.80, 0.82, 0.84, 0.85]
        self.fdn.allpass_delays_ms = [5.5, 7.5]
        self.fdn.allpass_feedbacks = [0.71, 0.76]
        
        self._update_fdn()
        
        self.early_reflections.taps = [
            (20.0, 0.58, 0.48),
            (45.0, 0.52, 0.52),
            (70.0, 0.48, 0.58),
            (100.0, 0.42, 0.6),
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
    print("Testing Mode1983 (AKG ADR68K)...")
    mode = Mode1983(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1983 test completed successfully!')
