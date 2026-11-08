"""
Verb Mode Base Class

Base class for all Isengard Verb modes.

Each mode subclass implements specific FDN parameters and early reflection
patterns based on the reference hardware/algorithm.

Integrates:
- FDN reverb
- Early reflections
- Modulation matrix
- Color system
"""

import numpy as np
from typing import Tuple, List, Dict, Any
from abc import ABC, abstractmethod

from isengard_verb.dsp.fdn import FDNReverb
from isengard_verb.dsp.early_reflections import EarlyReflections
from isengard_verb.dsp.modulation import ModulationMatrix
from isengard_verb.dsp.color import ColorSystem


class VerbModeBase(ABC):
    """
    Base class for all Isengard Verb modes.
    
    Each mode has unique characteristics:
    - FDN parameters (comb delays, feedbacks, allpass settings)
    - Early reflection patterns
    - Modulation characteristics
    - Damping characteristics
    
    The color system modifies these characteristics based on the era.
    """
    
    # Mode metadata
    name: str = "Base"
    year: int = 1970
    description: str = "Base verb mode"
    category: str = "Generic"  # Plate, Hall, Room, Ambience, Modern
    
    # Default parameters
    DEFAULT_PARAMS: Dict[str, Any] = {
        'decay': 0.5,
        'size': 0.5,
        'damping': 0.5,
        'damping_freq': 10000.0,
        'diffusion': 0.5,
        'mod_rate': 0.5,
        'mod_depth': 0.1,
        'pre_delay': 50.0,
        'early_level': 0.5,
        'width': 0.5,
        'attack': 0.0,
        'bass_mult': 1.0,
        'bass_xover': 200.0,
        'high_cut': 10000.0,
        'color': '1980s',  # Color system: '1970s', '1980s', 'Now'
    }
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize the verb mode.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        
        # Create FDN reverb
        self.fdn = FDNReverb(sample_rate=sample_rate)
        
        # Create early reflections
        self.early_reflections = EarlyReflections(sample_rate=sample_rate)
        
        # Create modulation matrix
        self.modulation = ModulationMatrix(sample_rate=sample_rate)
        
        # Create color system
        self.color_system = ColorSystem()
        
        # Parameters
        self.params = self.DEFAULT_PARAMS.copy()
        
        # Mode-specific initialization
        self._init_mode()
        
        # Apply color system
        self._apply_color()
    
    def _init_mode(self):
        """
        Initialize mode-specific parameters.
        
        Override this in subclasses to set mode-specific FDN parameters,
        early reflection patterns, etc.
        """
        # Default: 4 combs, 2 allpasses
        # Subclasses should override this
        pass
    
    def _apply_color(self):
        """Apply color system modifications to parameters."""
        color = self.params.get('color', '1980s')
        self.color_system.set_color(color)
        
        # Get color-specific parameters
        color_params = self.color_system.get_color_params()
        
        # Apply color modifications to our parameters
        for key, value in color_params.items():
            if key in self.params:
                # For multiplicative parameters
                if key in ['damping', 'diffusion', 'mod_rate', 'mod_depth', 'bass_mult']:
                    self.params[key] = self.params[key] * value
                else:
                    # For additive/replacement parameters
                    self.params[key] = value
        
        # Update FDN and early reflections with color-modified parameters
        self._update_fdn()
        self._update_early_reflections()
        self._update_modulation()
    
    def _update_fdn(self):
        """Update FDN parameters from self.params."""
        fdn_params = {}
        for key in ['decay', 'size', 'damping', 'damping_freq', 'diffusion', 'mod_rate', 'mod_depth']:
            if key in self.params:
                fdn_params[key] = self.params[key]
        self.fdn.set_parameters(fdn_params)
        
        # Also update the comb/allpass delays if they were set in _init_mode
        if hasattr(self, '_comb_delays_set') and self._comb_delays_set:
            # These were already set in _init_mode, so we don't need to update
            pass
    
    def _update_early_reflections(self):
        """Update early reflections parameters from self.params."""
        er_params = {}
        for key in ['size', 'width', 'pre_delay', 'early_level']:
            if key in self.params:
                er_params[key] = self.params[key]
        self.early_reflections.set_parameters(er_params)
        
        # Set mode-specific taps
        self.early_reflections.set_mode(self.name)
    
    def _update_modulation(self):
        """Update modulation parameters from self.params."""
        mod_params = {}
        for key in ['mod_rate', 'mod_depth']:
            if key in self.params:
                mod_params[key] = self.params[key]
        self.modulation.set_parameters(mod_params)
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the mode name."""
        return self.name
    
    @abstractmethod
    def get_year(self) -> int:
        """Get the year/era of this mode."""
        return self.year
    
    @abstractmethod
    def get_description(self) -> str:
        """Get a description of this mode."""
        return self.description
    
    @abstractmethod
    def get_category(self) -> str:
        """Get the category of this mode."""
        return self.category
    
    def reset(self):
        """Reset all internal state."""
        self.fdn.reset()
        self.early_reflections.reset()
        self.modulation.reset()
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        self.fdn.set_sample_rate(sample_rate)
        self.early_reflections.set_sample_rate(sample_rate)
        self.modulation.set_sample_rate(sample_rate)
    
    def set_parameters(self, params: Dict[str, Any]):
        """Set all parameters at once."""
        for key, value in params.items():
            if key in self.params:
                self.params[key] = value
        
        # Re-apply color system if color changed
        if 'color' in params:
            self._apply_color()
        
        # Update components
        self._update_fdn()
        self._update_early_reflections()
        self._update_modulation()
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get current parameters."""
        return self.params.copy()
    
    def set_color(self, color: str):
        """Set the color system."""
        self.params['color'] = color
        self._apply_color()
    
    def get_color(self) -> str:
        """Get the current color."""
        return self.params.get('color', '1980s')
    
    def process_sample(self, input_l: float, input_r: float) -> Tuple[float, float]:
        """
        Process a single stereo sample through the verb mode.
        
        Signal flow:
        1. Early reflections
        2. FDN reverb (late reverb)
        3. Mix early and late
        
        Args:
            input_l: Left input sample
            input_r: Right input sample
            
        Returns:
            Tuple of (output_l, output_r)
        """
        # Process early reflections
        er_l, er_r = self.early_reflections.process_sample(input_l, input_r)
        
        # Process FDN (late reverb)
        # Convert stereo to mono for FDN, then back to stereo
        input_mono = (input_l + input_r) * 0.5
        fdn_out = self.fdn.process_sample(input_mono)
        
        # Mix early and late
        early_level = self.params.get('early_level', 0.5)
        late_level = 1.0 - early_level
        
        output_l = er_l * early_level + fdn_out * late_level
        output_r = er_r * early_level + fdn_out * late_level
        
        return output_l, output_r
    
    def process_block(self, input_block: np.ndarray) -> np.ndarray:
        """
        Process a block of stereo audio samples.
        
        Args:
            input_block: Input audio as numpy array (N, 2)
            
        Returns:
            Output audio as numpy array (N, 2)
        """
        num_samples = input_block.shape[0]
        output_block = np.zeros((num_samples, 2), dtype=np.float32)
        
        for i in range(num_samples):
            output_l, output_r = self.process_sample(input_block[i, 0], input_block[i, 1])
            output_block[i, 0] = output_l
            output_block[i, 1] = output_r
        
        return output_block
    
    def get_impulse_response(self, duration_seconds: float = 3.0) -> np.ndarray:
        """
        Generate an impulse response for this mode.
        
        Args:
            duration_seconds: Duration of the impulse response
            
        Returns:
            Impulse response as numpy array (N, 2)
        """
        num_samples = int(duration_seconds * self.sample_rate)
        input_block = np.zeros((num_samples, 2), dtype=np.float32)
        input_block[0, 0] = 1.0  # Impulse on left channel
        input_block[0, 1] = 1.0  # Impulse on right channel
        
        return self.process_block(input_block)


# Test
if __name__ == "__main__":
    print("Testing VerbModeBase...")
    print("This is an abstract base class - test subclasses instead.")
