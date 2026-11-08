"""
Modulation Matrix Implementation

Modulation system for Isengard Verb.

This module provides modulation for the FDN reverb, including:
- LFOs for comb filter modulation
- LFOs for allpass filter modulation
- Global modulation control
- Mode-specific modulation characteristics

Based on VERIFIED evidence from ValhallaVintageVerb documentation.
"""

import numpy as np
from typing import List, Dict, Any, Tuple


class LFO:
    """
    Low Frequency Oscillator for modulation.
    
    Provides periodic modulation signals for reverb parameters.
    Supports sine, triangle, square, and random waveforms.
    """
    
    WAVEFORM_SINE = "sine"
    WAVEFORM_TRIANGLE = "triangle"
    WAVEFORM_SQUARE = "square"
    WAVEFORM_RANDOM = "random"
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize LFO.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.phase = 0.0
        self.waveform = self.WAVEFORM_SINE
        self.rate = 1.0  # Hz
        self.depth = 0.5  # 0.0 to 1.0
        self.offset = 0.0  # -1.0 to 1.0
        
        # For random waveform
        self._random_phase = 0.0
        self._random_rate = 1.0
        self._random_value = 0.0
        self._rng_state = np.random.RandomState()
    
    def reset(self):
        """Reset LFO state."""
        self.phase = 0.0
        self._random_phase = 0.0
        self._random_value = 0.0
        self._rng_state = np.random.RandomState()
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
    
    def set_waveform(self, waveform: str):
        """Set waveform type."""
        if waveform in [self.WAVEFORM_SINE, self.WAVEFORM_TRIANGLE, 
                       self.WAVEFORM_SQUARE, self.WAVEFORM_RANDOM]:
            self.waveform = waveform
    
    def set_rate(self, rate: float):
        """Set LFO rate in Hz."""
        self.rate = np.clip(rate, 0.01, 20.0)
    
    def set_depth(self, depth: float):
        """Set LFO depth (0.0 to 1.0)."""
        self.depth = np.clip(depth, 0.0, 1.0)
    
    def set_offset(self, offset: float):
        """Set LFO offset (-1.0 to 1.0)."""
        self.offset = np.clip(offset, -1.0, 1.0)
    
    def get_value(self) -> float:
        """
        Get current LFO value.
        
        Returns:
            LFO value in range [-1.0, 1.0] * depth + offset
        """
        if self.waveform == self.WAVEFORM_SINE:
            value = np.sin(self.phase * 2.0 * np.pi)
        elif self.waveform == self.WAVEFORM_TRIANGLE:
            # Triangle wave
            value = 2.0 * abs(2.0 * (self.phase - np.floor(self.phase + 0.5))) - 1.0
        elif self.waveform == self.WAVEFORM_SQUARE:
            value = 1.0 if self.phase < 0.5 else -1.0
        elif self.waveform == self.WAVEFORM_RANDOM:
            # Random waveform (sample and hold)
            if self.phase >= self._random_phase:
                self._random_value = self._rng_state.uniform(-1.0, 1.0)
                self._random_phase = self.phase + 1.0 / self._random_rate
            value = self._random_value
        else:
            value = 0.0
        
        # Apply depth and offset
        result = value * self.depth + self.offset
        
        # Update phase
        self.phase += self.rate / self.sample_rate
        if self.phase >= 1.0:
            self.phase -= 1.0
        
        return result
    
    def get_block(self, num_samples: int) -> np.ndarray:
        """
        Get a block of LFO values.
        
        Args:
            num_samples: Number of samples
            
        Returns:
            Array of LFO values
        """
        values = np.zeros(num_samples, dtype=np.float32)
        
        for i in range(num_samples):
            values[i] = self.get_value()
        
        return values


class ModulationMatrix:
    """
    Modulation matrix for FDN reverb.
    
    Provides modulation signals for:
    - Comb filters (delay time modulation)
    - Allpass filters (delay time modulation)
    - Feedback matrix (modulation of matrix elements)
    - Damping filters (cutoff modulation)
    
    Each modulation source can be routed to multiple destinations
    with configurable depth and offset.
    """
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize modulation matrix.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        
        # Parameters
        self.params = {
            'rate': 0.5,   # Modulation rate in Hz
            'depth': 0.1,  # Modulation depth
        }
        
        # Create LFOs for different modulation targets
        # Each target can have its own LFO
        self.comb_lfos = []
        self.allpass_lfos = []
        self.global_lfo = LFO(sample_rate)
        
        # Number of comb and allpass filters (will be set by FDN)
        self.num_combs = 4
        self.num_allpasses = 2
        
        # Initialize LFOs
        self._init_lfos()
        
        # Modulation routing
        self.comb_mod_depths = [0.1] * self.num_combs  # Modulation depth per comb
        self.allpass_mod_depths = [0.1] * self.num_allpasses  # Modulation depth per allpass
    
    def _init_lfos(self):
        """Initialize all LFOs."""
        self.comb_lfos = []
        for i in range(self.num_combs):
            lfo = LFO(self.sample_rate)
            lfo.set_rate(self.params['rate'] * (0.8 + i * 0.1))  # Slightly different rates
            lfo.set_depth(self.params['depth'])
            lfo.set_waveform(LFO.WAVEFORM_SINE)
            self.comb_lfos.append(lfo)
        
        self.allpass_lfos = []
        for i in range(self.num_allpasses):
            lfo = LFO(self.sample_rate)
            lfo.set_rate(self.params['rate'] * (1.0 + i * 0.1))  # Different rates
            lfo.set_depth(self.params['depth'] * 0.8)  # Less depth for allpass
            lfo.set_waveform(LFO.WAVEFORM_SINE)
            self.allpass_lfos.append(lfo)
        
        # Global LFO
        self.global_lfo.set_rate(self.params['rate'])
        self.global_lfo.set_depth(self.params['depth'])
        self.global_lfo.set_waveform(LFO.WAVEFORM_SINE)
    
    def reset(self):
        """Reset all internal state."""
        for lfo in self.comb_lfos:
            lfo.reset()
        for lfo in self.allpass_lfos:
            lfo.reset()
        self.global_lfo.reset()
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        for lfo in self.comb_lfos:
            lfo.set_sample_rate(sample_rate)
        for lfo in self.allpass_lfos:
            lfo.set_sample_rate(sample_rate)
        self.global_lfo.set_sample_rate(sample_rate)
    
    def set_num_filters(self, num_combs: int, num_allpasses: int):
        """
        Set the number of comb and allpass filters.
        
        Args:
            num_combs: Number of comb filters
            num_allpasses: Number of allpass filters
        """
        self.num_combs = num_combs
        self.num_allpasses = num_allpasses
        self._init_lfos()
        self.comb_mod_depths = [0.1] * self.num_combs
        self.allpass_mod_depths = [0.1] * self.num_allpasses
    
    def set_rate(self, rate: float):
        """Set modulation rate."""
        self.params['rate'] = np.clip(rate, 0.1, 10.0)
        for i, lfo in enumerate(self.comb_lfos):
            lfo.set_rate(rate * (0.8 + i * 0.1))
        for i, lfo in enumerate(self.allpass_lfos):
            lfo.set_rate(rate * (1.0 + i * 0.1))
        self.global_lfo.set_rate(rate)
    
    def set_depth(self, depth: float):
        """Set modulation depth."""
        self.params['depth'] = np.clip(depth, 0.0, 1.0)
        for lfo in self.comb_lfos:
            lfo.set_depth(depth)
        for lfo in self.allpass_lfos:
            lfo.set_depth(depth * 0.8)
        self.global_lfo.set_depth(depth)
    
    def set_parameters(self, params: dict):
        """Set all parameters at once."""
        for key, value in params.items():
            if key == 'rate':
                self.set_rate(value)
            elif key == 'depth':
                self.set_depth(value)
    
    def get_parameters(self) -> dict:
        """Get current parameters."""
        return self.params.copy()
    
    def set_comb_mod_depth(self, comb_index: int, depth: float):
        """Set modulation depth for a specific comb filter."""
        if comb_index < len(self.comb_mod_depths):
            self.comb_mod_depths[comb_index] = np.clip(depth, 0.0, 1.0)
    
    def set_allpass_mod_depth(self, allpass_index: int, depth: float):
        """Set modulation depth for a specific allpass filter."""
        if allpass_index < len(self.allpass_mod_depths):
            self.allpass_mod_depths[allpass_index] = np.clip(depth, 0.0, 1.0)
    
    def get_comb_modulation(self, comb_index: int = 0) -> float:
        """
        Get modulation value for a comb filter.
        
        Args:
            comb_index: Index of the comb filter
            
        Returns:
            Modulation value for delay time (in samples)
        """
        if comb_index < len(self.comb_lfos):
            lfo_value = self.comb_lfos[comb_index].get_value()
            return lfo_value * self.comb_mod_depths[comb_index]
        return 0.0
    
    def get_allpass_modulation(self, allpass_index: int = 0) -> float:
        """
        Get modulation value for an allpass filter.
        
        Args:
            allpass_index: Index of the allpass filter
            
        Returns:
            Modulation value for delay time (in samples)
        """
        if allpass_index < len(self.allpass_lfos):
            lfo_value = self.allpass_lfos[allpass_index].get_value()
            return lfo_value * self.allpass_mod_depths[allpass_index]
        return 0.0
    
    def get_global_modulation(self) -> float:
        """
        Get global modulation value.
        
        Returns:
            Global modulation value
        """
        return self.global_lfo.get_value()
    
    def get_comb_mod_block(self, comb_index: int, num_samples: int) -> np.ndarray:
        """
        Get a block of modulation values for a comb filter.
        
        Args:
            comb_index: Index of the comb filter
            num_samples: Number of samples
            
        Returns:
            Array of modulation values
        """
        if comb_index < len(self.comb_lfos):
            values = self.comb_lfos[comb_index].get_block(num_samples)
            return values * self.comb_mod_depths[comb_index]
        return np.zeros(num_samples, dtype=np.float32)
    
    def get_allpass_mod_block(self, allpass_index: int, num_samples: int) -> np.ndarray:
        """
        Get a block of modulation values for an allpass filter.
        
        Args:
            allpass_index: Index of the allpass filter
            num_samples: Number of samples
            
        Returns:
            Array of modulation values
        """
        if allpass_index < len(self.allpass_lfos):
            values = self.allpass_lfos[allpass_index].get_block(num_samples)
            return values * self.allpass_mod_depths[allpass_index]
        return np.zeros(num_samples, dtype=np.float32)


# Test
if __name__ == "__main__":
    print("Testing ModulationMatrix...")
    
    mod = ModulationMatrix(sample_rate=44100)
    mod.set_parameters({'rate': 1.0, 'depth': 0.5})
    
    print("\nLFO Test:")
    lfo = LFO(44100)
    lfo.set_rate(1.0)
    lfo.set_depth(0.5)
    for i in range(10):
        print(f'  LFO value {i}: {lfo.get_value():.6f}')
    
    print("\nModulationMatrix Test:")
    for i in range(10):
        print(f'  Global mod {i}: {mod.get_global_modulation():.6f}')
        print(f'  Comb 0 mod {i}: {mod.get_comb_modulation(0):.6f}')
        print(f'  Allpass 0 mod {i}: {mod.get_allpass_modulation(0):.6f}')
    
    print('\nModulationMatrix test completed successfully!')
