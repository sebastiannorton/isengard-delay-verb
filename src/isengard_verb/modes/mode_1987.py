"""
Mode 1987 - Lexicon 480L

Based on the Lexicon 480L (1987).

Characteristics:
- High-end Lexicon reverb
- Rich, lush sound
- Complex algorithms
- Studio standard

Category: Hall
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1987(VerbModeBase):
    """
    Lexicon 480L (1987).
    
    The Lexicon 480L was a high-end digital reverb that became
    a studio standard with its rich, lush sound and complex algorithms.
    """
    
    name = "1987"
    year = 1987
    description = "Lexicon 480L - High-end digital reverb with rich, lush sound and complex algorithms"
    category = "Hall"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.7,
        'size': 0.8,
        'damping': 0.4,
        'damping_freq': 12000.0,
        'diffusion': 0.8,
        'mod_rate': 0.3,
        'mod_depth': 0.15,
        'pre_delay': 80.0,
        'early_level': 0.4,
        'width': 0.8,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Lexicon 480L-specific parameters."""
        # 480L had more complex FDN with longer delays
        self.fdn.comb_delays_ms = [1300.0, 1500.0, 1700.0, 1900.0]
        self.fdn.comb_feedbacks = [0.83, 0.85, 0.87, 0.89]
        self.fdn.allpass_delays_ms = [7.0, 9.0]
        self.fdn.allpass_feedbacks = [0.73, 0.78]
        
        self._update_fdn()
        
        # 480L had sophisticated early reflections
        self.early_reflections.taps = [
            (20.0, 0.6, 0.4),
            (45.0, 0.55, 0.45),
            (75.0, 0.5, 0.5),
            (110.0, 0.45, 0.55),
            (150.0, 0.4, 0.6),
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
    print("Testing Mode1987 (Lexicon 480L)...")
    mode = Mode1987(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1987 test completed successfully!')
