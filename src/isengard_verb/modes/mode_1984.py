"""
Mode 1984 - Roland SRV-2000

Based on the Roland SRV-2000 (1984).

Characteristics:
- Roland's early digital reverb
- Warm, musical sound
- Good for drums and percussion
- Characteristic Roland tone

Category: Room
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1984(VerbModeBase):
    """
    Roland SRV-2000 (1984).
    
    The Roland SRV-2000 was Roland's early digital reverb,
    known for its warm, musical sound and good drum performance.
    """
    
    name = "1984"
    year = 1984
    description = "Roland SRV-2000 - Warm, musical digital reverb with characteristic Roland tone"
    category = "Room"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.62,
        'size': 0.68,
        'damping': 0.52,
        'damping_freq': 9500.0,
        'diffusion': 0.72,
        'mod_rate': 0.32,
        'mod_depth': 0.13,
        'pre_delay': 65.0,
        'early_level': 0.48,
        'width': 0.68,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Roland SRV-2000-specific parameters."""
        self.fdn.comb_delays_ms = [950.0, 1150.0, 1350.0, 1550.0]
        self.fdn.comb_feedbacks = [0.81, 0.83, 0.85, 0.87]
        self.fdn.allpass_delays_ms = [6.0, 8.0]
        self.fdn.allpass_feedbacks = [0.7, 0.75]
        
        self._update_fdn()
        
        self.early_reflections.taps = [
            (30.0, 0.55, 0.5),
            (60.0, 0.5, 0.55),
            (90.0, 0.45, 0.6),
            (120.0, 0.4, 0.65),
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
    print("Testing Mode1984 (Roland SRV-2000)...")
    mode = Mode1984(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1984 test completed successfully!')
