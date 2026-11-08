"""
Unified Verb Processor

This module provides the complete Isengard Verb processing chain:
Input -> Early Reflections -> FDN Reverb -> Output

With integrated:
- Mode selection (22 modes)
- Color system (1970s, 1980s, Now)
- Parameter smoothing
- Dry/wet mix
- Input/output filtering
"""

import numpy as np
from typing import Tuple, Dict, Any, Optional

from .modes import get_mode, list_modes, VerbModeBase
from .dsp.color import ColorSystem
from .dsp.fdn import FDNReverb
from .dsp.early_reflections import EarlyReflections
from .dsp.modulation import ModulationMatrix
from isengard_shared.filters import OnePoleFilter, BiquadFilter
from isengard_shared.params import SmoothedParameter


class VerbProcessor:
    """
    Unified reverb processor for Isengard Verb.
    
    Combines all components into a single processing chain:
    1. Input filtering (high-pass, low-pass)
    2. Early reflections
    3. FDN reverb (late reflections)
    4. Output filtering
    5. Dry/wet mix
    
    Parameters:
        mode: Reverb mode (1972, 1978, 1987, NOW1, etc.)
        color: Color setting (1970s, 1980s, Now)
        mix: Dry/wet mix (0.0 = dry, 1.0 = wet)
        decay: Decay time
        size: Room size
        damping: High-frequency damping
        damping_freq: Damping frequency
        diffusion: Diffusion amount
        mod_rate: Modulation rate
        mod_depth: Modulation depth
        pre_delay: Pre-delay time
        early_level: Early reflection level
        width: Stereo width
        high_cut: High-frequency cutoff
        low_cut: Low-frequency cutoff
        attack: Attack time
        bass_mult: Bass multiplier
        bass_xover: Bass crossover frequency
    """
    
    # Default parameters
    DEFAULT_PARAMS: Dict[str, Any] = {
        'mode': '1978',
        'color': '1980s',
        'mix': 0.5,
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
        'high_cut': 10000.0,
        'low_cut': 200.0,
        'attack': 0.0,
        'bass_mult': 1.0,
        'bass_xover': 200.0,
    }
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize the verb processor.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        
        # Create components
        self.color_system = ColorSystem()
        self.early_reflections = EarlyReflections(sample_rate=sample_rate)
        self.fdn = FDNReverb(sample_rate=sample_rate)
        self.modulation = ModulationMatrix(sample_rate=sample_rate)
        
        # Create mode instance (will be updated when mode changes)
        self.mode: Optional[VerbModeBase] = None
        self._current_mode_name: str = self.DEFAULT_PARAMS['mode']
        
        # Input/output filters
        self.input_highpass = OnePoleFilter(
            cutoff_hz=20.0,
            sample_rate=sample_rate,
            filter_type='highpass'
        )
        self.input_lowpass = OnePoleFilter(
            cutoff_hz=20000.0,
            sample_rate=sample_rate,
            filter_type='lowpass'
        )
        self.output_highpass = OnePoleFilter(
            cutoff_hz=20.0,
            sample_rate=sample_rate,
            filter_type='highpass'
        )
        self.output_lowpass = OnePoleFilter(
            cutoff_hz=20000.0,
            sample_rate=sample_rate,
            filter_type='lowpass'
        )
        
        # Bass multiplier filter (for low-frequency enhancement)
        self.bass_filter = OnePoleFilter(
            cutoff_hz=200.0,
            sample_rate=sample_rate,
            filter_type='lowpass'
        )
        
        # Parameter smoothing
        self._create_smoothers()
        
        # Parameters
        self.params = self.DEFAULT_PARAMS.copy()
        
        # Internal state
        self._prev_input_l = 0.0
        self._prev_input_r = 0.0
        self._prev_output_l = 0.0
        self._prev_output_r = 0.0
        
        # Initialize with default mode
        self.set_mode(self.params['mode'])
        self.set_color(self.params['color'])
    
    def _create_smoothers(self):
        """Create smoothed parameters for click-free automation."""
        # Smoothing time constant (in milliseconds)
        smooth_time_ms = 10.0  # 10ms
        
        self.smoothers = {
            'mix': SmoothedParameter(0.5, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'decay': SmoothedParameter(0.5, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'size': SmoothedParameter(0.5, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'damping': SmoothedParameter(0.5, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'damping_freq': SmoothedParameter(10000.0, 100.0, 20000.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'diffusion': SmoothedParameter(0.5, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'mod_rate': SmoothedParameter(0.5, 0.1, 10.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'mod_depth': SmoothedParameter(0.1, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'pre_delay': SmoothedParameter(50.0, 0.0, 200.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'early_level': SmoothedParameter(0.5, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'width': SmoothedParameter(0.5, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'high_cut': SmoothedParameter(10000.0, 100.0, 20000.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'low_cut': SmoothedParameter(200.0, 20.0, 1000.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
        }
    
    def reset(self):
        """Reset all internal state."""
        self.early_reflections.reset()
        self.fdn.reset()
        self.modulation.reset()
        self.input_highpass.reset()
        self.input_lowpass.reset()
        self.output_highpass.reset()
        self.output_lowpass.reset()
        self.bass_filter.reset()
        
        for smoother in self.smoothers.values():
            smoother.reset()
        
        self._prev_input_l = 0.0
        self._prev_input_r = 0.0
        self._prev_output_l = 0.0
        self._prev_output_r = 0.0
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        self.early_reflections.set_sample_rate(sample_rate)
        self.fdn.set_sample_rate(sample_rate)
        self.modulation.set_sample_rate(sample_rate)
        self.input_highpass.set_sample_rate(sample_rate)
        self.input_lowpass.set_sample_rate(sample_rate)
        self.output_highpass.set_sample_rate(sample_rate)
        self.output_lowpass.set_sample_rate(sample_rate)
        self.bass_filter.set_sample_rate(sample_rate)
        
        # Recreate smoothers with new sample rate
        self._create_smoothers()
    
    def set_mode(self, mode_name: str):
        """
        Set the reverb mode.
        
        Args:
            mode_name: Mode name (e.g., '1978', 'NOW1')
        """
        if mode_name not in list_modes():
            raise ValueError(f"Unknown mode: {mode_name}. Available: {list_modes()}")
        
        self._current_mode_name = mode_name
        self.params['mode'] = mode_name
        
        # Create new mode instance
        self.mode = get_mode(mode_name, self.sample_rate)
        
        # Update color system in mode
        if self.mode:
            self.mode.set_color(self.params.get('color', '1980s'))
    
    def set_color(self, color: str):
        """
        Set the color system.
        
        Args:
            color: Color name ('1970s', '1980s', 'Now')
        """
        self.params['color'] = color
        self.color_system.set_color(color)
        
        # Update mode color
        if self.mode:
            self.mode.set_color(color)
    
    def set_parameters(self, params: Dict[str, Any]):
        """
        Set all parameters at once.
        
        Args:
            params: Dictionary of parameter name -> value
        """
        for key, value in params.items():
            if key in self.params:
                self.params[key] = value
        
        # Update mode if it exists
        if self.mode:
            mode_params = {k: v for k, v in params.items() if k in self.mode.DEFAULT_PARAMS}
            if mode_params:
                self.mode.set_parameters(mode_params)
        
        # Update color
        if 'color' in params:
            self.set_color(params['color'])
        
        # Update mode
        if 'mode' in params:
            self.set_mode(params['mode'])
        
        # Update filters
        if 'high_cut' in params:
            self.output_lowpass.set_cutoff(params['high_cut'])
        if 'low_cut' in params:
            self.input_highpass.set_cutoff(params['low_cut'])
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get current parameters."""
        return self.params.copy()
    
    def _get_smoothed_params(self) -> Dict[str, float]:
        """Get smoothed parameter values."""
        smoothed = {}
        for key, smoother in self.smoothers.items():
            if key in self.params:
                # Set target value
                smoother.target_value = self.params[key]
                # Get smoothed value
                smoothed[key] = smoother.get_value()
                # Process one sample
                smoother.process_sample()
            else:
                smoothed[key] = smoother.get_value()
        return smoothed
    
    def process_sample(self, input_l: float, input_r: float) -> Tuple[float, float]:
        """
        Process a single stereo sample.
        
        Signal flow:
        1. Input filtering (high-pass, low-pass)
        2. Early reflections
        3. FDN reverb (late reflections)
        4. Bass enhancement (optional)
        5. Output filtering
        6. Dry/wet mix
        
        Args:
            input_l: Left input sample
            input_r: Right input sample
            
        Returns:
            Tuple of (output_l, output_r)
        """
        # Get smoothed parameters
        smoothed = self._get_smoothed_params()
        
        # Apply input filtering
        input_l_filtered = self.input_highpass.process(input_l)
        input_l_filtered = self.input_lowpass.process(input_l_filtered)
        input_r_filtered = self.input_highpass.process(input_r)
        input_r_filtered = self.input_lowpass.process(input_r_filtered)
        
        # Process through mode (early reflections + FDN)
        if self.mode:
            # Update mode parameters with smoothed values
            mode_params = {
                'decay': smoothed.get('decay', 0.5),
                'size': smoothed.get('size', 0.5),
                'damping': smoothed.get('damping', 0.5),
                'damping_freq': smoothed.get('damping_freq', 10000.0),
                'diffusion': smoothed.get('diffusion', 0.5),
                'mod_rate': smoothed.get('mod_rate', 0.5),
                'mod_depth': smoothed.get('mod_depth', 0.1),
                'pre_delay': smoothed.get('pre_delay', 50.0),
                'early_level': smoothed.get('early_level', 0.5),
                'width': smoothed.get('width', 0.5),
            }
            self.mode.set_parameters(mode_params)
            
            # Process through mode
            verb_l, verb_r = self.mode.process_sample(input_l_filtered, input_r_filtered)
        else:
            # Fallback: simple pass-through
            verb_l, verb_r = input_l_filtered, input_r_filtered
        
        # Apply bass enhancement
        bass_mult = smoothed.get('bass_mult', 1.0)
        if bass_mult != 1.0:
            bass_l = self.bass_filter.process(input_l_filtered)
            bass_r = self.bass_filter.process(input_r_filtered)
            verb_l += bass_l * (bass_mult - 1.0)
            verb_r += bass_r * (bass_mult - 1.0)
        
        # Apply output filtering
        output_l = self.output_highpass.process(verb_l)
        output_l = self.output_lowpass.process(output_l)
        output_r = self.output_highpass.process(verb_r)
        output_r = self.output_lowpass.process(output_r)
        
        # Apply dry/wet mix
        mix = smoothed.get('mix', 0.5)
        dry_l = input_l
        dry_r = input_r
        wet_l = output_l
        wet_r = output_r
        
        output_l = dry_l * (1.0 - mix) + wet_l * mix
        output_r = dry_r * (1.0 - mix) + wet_r * mix
        
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
            output_l, output_r = self.process_sample(
                input_block[i, 0], 
                input_block[i, 1]
            )
            output_block[i, 0] = output_l
            output_block[i, 1] = output_r
        
        return output_block
    
    def get_impulse_response(self, duration_seconds: float = 3.0) -> np.ndarray:
        """
        Generate an impulse response.
        
        Args:
            duration_seconds: Duration of the impulse response
            
        Returns:
            Impulse response as numpy array (N, 2)
        """
        num_samples = int(duration_seconds * self.sample_rate)
        input_block = np.zeros((num_samples, 2), dtype=np.float32)
        input_block[0, 0] = 1.0
        input_block[0, 1] = 1.0
        
        return self.process_block(input_block)
    
    def list_modes(self) -> list:
        """List all available modes."""
        return list_modes()
    
    def list_colors(self) -> list:
        """List all available colors."""
        return self.color_system.list_colors()


# Test
if __name__ == "__main__":
    print("Testing VerbProcessor...")
    
    # Create processor
    processor = VerbProcessor(sample_rate=44100)
    
    # Test with different modes
    for mode in ['1972', '1978', '1987', 'NOW1']:
        print(f"\nMode: {mode}")
        processor.set_mode(mode)
        
        # Set some parameters
        processor.set_parameters({
            'mix': 1.0,  # Full wet
            'decay': 0.7,
            'size': 0.8,
        })
        
        # Generate impulse response
        ir = processor.get_impulse_response(duration_seconds=1.0)
        print(f'  IR shape: {ir.shape}')
        print(f'  IR peak: {np.max(np.abs(ir)):.6f}')
        print(f'  IR RMS: {np.sqrt(np.mean(ir**2)):.6f}')
    
    # Test parameter smoothing
    print("\nTesting parameter smoothing...")
    processor.set_parameters({'mix': 0.0})
    for i in range(10):
        processor.process_sample(0.5, 0.5)
    processor.set_parameters({'mix': 1.0})
    print("  Mix smoothed from 0.0 to 1.0 over 10 samples")
    
    print('\nVerbProcessor test completed successfully!')
