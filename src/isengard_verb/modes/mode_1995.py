"""
Mode 1995 - Yamaha SPX90

Based on the Yamaha SPX90 (1995).

Characteristics:
- Popular Yamaha effects processor
- Good reverb algorithms
- Affordable and versatile
- Characteristic Yamaha sound

Category: Room
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1995(VerbModeBase):
    """
    Yamaha SPX90 (1995).
    
    The Yamaha SPX90 was a popular effects processor with
    good reverb algorithms, known for being affordable and versatile.
    """
    
    name = "1995"
    year = 1995
    description = "Yamaha SPX90 - Popular effects processor with good reverb algorithms"
    category = "Room"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.58,
        'size': 0.65,
        'damping': 0.48,
        'damping_freq': 10500.0,
        'diffusion': 0.7,
        'mod_rate': 0.4,
        'mod_depth': 0.1,
        'pre_delay': 55.0,
        'early_level': 0.52,
        'width': 0.7,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Yamaha SPX90-specific parameters."""
        self.fdn.comb_delays_ms = [850.0, 1050.0, 1250.0, 1450.0]
        self.fdn.comb_feedbacks = [0.79, 0.81, 0.83, 0.85]
        self.fdn.allpass_delays_ms = [5.5, 7.5]
        self.fdn.allpass_feedbacks = [0.69, 0.74]
        
        self._update_fdn()
        
        self.early_reflections.taps = [
            (20.0, 0.6, 0.4),
            (45.0, 0.55, 0.45),
            (75.0, 0.5, 0.5),
            (110.0, 0.45, 0.55),
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
    print("Testing Mode1995 (Yamaha SPX90)...")
    mode = Mode1995(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1995 test completed successfully!')
