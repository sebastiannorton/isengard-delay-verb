"""
Mode 1994 - Lexicon PCM80

Based on the Lexicon PCM80 (1994).

Characteristics:
- Classic Lexicon effects processor
- High-quality reverb algorithms
- Versatile and reliable
- Characteristic Lexicon sound

Category: Hall
"""

import numpy as np
from typing import Tuple

from .base import VerbModeBase


class Mode1994(VerbModeBase):
    """
    Lexicon PCM80 (1994).
    
    The Lexicon PCM80 was a classic effects processor with
    high-quality reverb algorithms and characteristic Lexicon sound.
    """
    
    name = "1994"
    year = 1994
    description = "Lexicon PCM80 - Classic effects processor with high-quality reverb algorithms"
    category = "Hall"
    
    DEFAULT_PARAMS = {
        **VerbModeBase.DEFAULT_PARAMS,
        'decay': 0.65,
        'size': 0.75,
        'damping': 0.42,
        'damping_freq': 11500.0,
        'diffusion': 0.78,
        'mod_rate': 0.32,
        'mod_depth': 0.14,
        'pre_delay': 80.0,
        'early_level': 0.42,
        'width': 0.78,
    }
    
    def __init__(self, sample_rate: int = 44100):
        super().__init__(sample_rate)
    
    def _init_mode(self):
        """Initialize Lexicon PCM80-specific parameters."""
        self.fdn.comb_delays_ms = [1200.0, 1400.0, 1600.0, 1800.0]
        self.fdn.comb_feedbacks = [0.82, 0.84, 0.86, 0.88]
        self.fdn.allpass_delays_ms = [7.0, 9.0]
        self.fdn.allpass_feedbacks = [0.72, 0.77]
        
        self._update_fdn()
        
        self.early_reflections.taps = [
            (25.0, 0.56, 0.45),
            (55.0, 0.51, 0.5),
            (90.0, 0.47, 0.53),
            (130.0, 0.42, 0.58),
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
    print("Testing Mode1994 (Lexicon PCM80)...")
    mode = Mode1994(sample_rate=44100)
    ir = mode.get_impulse_response(duration_seconds=2.0)
    print(f'IR peak: {np.max(np.abs(ir)):.6f}')
    print('Mode1994 test completed successfully!')
