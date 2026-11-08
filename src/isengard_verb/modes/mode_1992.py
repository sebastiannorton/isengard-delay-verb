"""
Mode 1992 - Eventide H3000

Based on the Eventide H3000 (1992).

Characteristics:
- Advanced harmonizer with reverb
- Complex algorithms
- Unique spatial effects
- Characteristic Eventide sound

Category: Ambience
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1992(VerbModeBase):
    """
    Eventide H3000 (1992).
    
    The Eventide H3000 was an advanced harmonizer that included
    sophisticated reverb algorithms with unique spatial characteristics.
    """
    
    name = "1992"
    year = 1992
    description = "Eventide H3000 - Advanced harmonizer with complex reverb and spatial effects"
    category = "Ambience"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.68,
        'size': 0.75,
        'damping': 0.38,
        'damping_freq': 13000.0,
        'diffusion': 0.8,
        'mod_rate': 0.25,
        'mod_depth': 0.18,
        'pre_delay': 85.0,
        'early_level': 0.35,
        'width': 0.85,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Eventide H3000-specific parameters."""
        # H3000 had very complex routing
        self.fdn.comb_delays_ms = [1400.0, 1600.0, 1800.0, 2000.0]
        self.fdn.comb_feedbacks = [0.84, 0.86, 0.88, 0.90]
        self.fdn.allpass_delays_ms = [8.0, 10.0]
        self.fdn.allpass_feedbacks = [0.75, 0.80]
        
        self._update_fdn()
        
        # H3000 had unique early reflection patterns
        self.early_reflections.taps = [
            (15.0, 0.55, 0.4),
            (40.0, 0.5, 0.45),
            (70.0, 0.45, 0.5),
            (120.0, 0.4, 0.55),
            (180.0, 0.35, 0.6),
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
    print("Testing Mode1992 (Eventide H3000)...")
    mode = Mode1992(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1992 test completed successfully!')
