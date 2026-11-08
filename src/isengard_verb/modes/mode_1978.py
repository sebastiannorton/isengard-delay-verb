"""
Mode 1978 - Lexicon 224

Based on the Lexicon 224 (1978).

Characteristics:
- Classic digital reverb
- Rich, dense decay
- Characteristic "Lexicon" sound
- Balanced early reflections

Category: Hall
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1978(VerbModeBase):
    """
    Lexicon 224 (1978).
    
    The Lexicon 224 is one of the most famous digital reverbs,
    known for its rich, dense sound and balanced characteristics.
    """
    
    name = "1978"
    year = 1978
    description = "Lexicon 224 - Classic digital reverb with rich, dense decay"
    category = "Hall"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.6,        # Medium-long decay
        'size': 0.7,         # Medium-large hall
        'damping': 0.5,
        'damping_freq': 10000.0,
        'diffusion': 0.7,    # High diffusion
        'mod_rate': 0.4,
        'mod_depth': 0.15,
        'pre_delay': 60.0,
        'early_level': 0.5,
        'width': 0.7,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Lexicon 224-specific parameters."""
        self.fdn.comb_delays_ms = [1000.0, 1200.0, 1400.0, 1600.0]
        self.fdn.comb_feedbacks = [0.80, 0.82, 0.84, 0.86]
        self.fdn.allpass_delays_ms = [6.0, 8.0]
        self.fdn.allpass_feedbacks = [0.7, 0.75]
        
        self._update_fdn()
        
        # Lexicon 224 had balanced early reflections
        self.early_reflections.taps = [
            (25.0, 0.6, 0.5),
            (50.0, 0.5, 0.6),
            (75.0, 0.5, 0.5),
            (100.0, 0.4, 0.6),
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
    print("Testing Mode1978 (Lexicon 224)...")
    mode = Mode1978(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1978 test completed successfully!')
