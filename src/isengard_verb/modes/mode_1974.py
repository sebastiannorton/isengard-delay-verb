"""
Mode 1974 - AMS RMX16 Digital Reverb

Based on the AMS RMX16 (1974).

Characteristics:
- Early digital reverb
- Characteristic "gated" sound
- Non-linear decay
- Distinct early reflection pattern

Category: Digital
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1974(VerbModeBase):
    """
    AMS RMX16 Digital Reverb (1974).
    
    The AMS RMX16 was an early digital reverb known for its
    characteristic gated reverb sound and non-linear decay.
    """
    
    name = "1974"
    year = 1974
    description = "AMS RMX16 - Early digital reverb with gated characteristics"
    category = "Digital"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.4,        # Shorter decay for gated sound
        'size': 0.5,         # Medium size
        'damping': 0.4,      # Less damping
        'damping_freq': 12000.0,
        'diffusion': 0.5,    # Moderate diffusion
        'mod_rate': 0.5,
        'mod_depth': 0.1,
        'pre_delay': 60.0,
        'early_level': 0.6,  # More early reflections
        'width': 0.7,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize AMS RMX16-specific parameters."""
        # RMX16 characteristics:
        # - Non-linear decay (gated)
        # - Distinct early reflection pattern
        
        self.fdn.comb_delays_ms = [800.0, 1000.0, 1200.0, 1400.0]
        self.fdn.comb_feedbacks = [0.75, 0.78, 0.80, 0.82]
        self.fdn.allpass_delays_ms = [4.0, 6.0]
        self.fdn.allpass_feedbacks = [0.65, 0.70]
        
        self._update_fdn()
        
        # RMX16 had a distinctive early reflection pattern
        self.early_reflections.taps = [
            (20.0, 0.7, 0.4),
            (40.0, 0.5, 0.7),
            (60.0, 0.4, 0.5),
            (80.0, 0.3, 0.6),
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
    print("Testing Mode1974 (AMS RMX16)...")
    mode = Mode1974(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1974 test completed successfully!')
