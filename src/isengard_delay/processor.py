"""
Unified Delay Processor

This module provides the complete Isengard Delay processing chain.

Combines:
- Mode selection (7 modes: Tape, HiFi, BBD, Digital, Ghost, Pitch, RevPitch)
- Style selection (5 styles: Single, Dual, Ratio, PingPong, Quad)
- Parameter smoothing
- Dry/wet mix
- Input/output filtering
"""

import numpy as np
from typing import Tuple, Dict, Any, Optional

from .modes import (
    TapeMode, HiFiMode, BBDMode, DigitalMode,
    GhostMode, PitchMode, RevPitchMode
)
from .styles import (
    SingleStyle, DualStyle, RatioStyle, PingPongStyle, QuadStyle
)
from isengard_shared.filters import OnePoleFilter
from isengard_shared.params import SmoothedParameter
from isengard_shared.delay_line import DelayLine


class DelayProcessor:
    """
    Unified delay processor for Isengard Delay.
    
    Combines mode and style into a single processing chain:
    1. Input filtering
    2. Mode processing (delay line, modulation, effects)
    3. Style routing (stereo handling)
    4. Output filtering
    5. Dry/wet mix
    
    Parameters:
        mode: Delay mode (tape, hifi, bbd, digital, ghost, pitch, revpitch)
        style: Delay style (single, dual, ratio, pingpong, quad)
        mix: Dry/wet mix (0.0 = dry, 1.0 = wet)
        feedback: Feedback amount
        delay_time_ms: Delay time in milliseconds
        delay_time_l_ms: Left delay time (for stereo modes)
        delay_time_r_ms: Right delay time (for stereo modes)
        ratio: Ratio for ratio mode
        spread: Stereo spread
        mod_rate: Modulation rate
        mod_depth: Modulation depth
        age: Age parameter (for digital mode)
        drive: Drive/saturation
        diffusion: Diffusion amount
        diffusion_size: Diffusion size
        eq_high: High EQ frequency
        eq_low: Low EQ frequency
        era: Era parameter (for ghost mode)
        ducking: Ducking amount
        pitch_shift: Pitch shift (for pitch mode)
        pitch_detune: Pitch detune (for pitch mode)
        frequency_shift: Frequency shift (for ghost mode)
    """
    
    # Mode classes
    MODE_CLASSES = {
        'tape': TapeMode,
        'hifi': HiFiMode,
        'bbd': BBDMode,
        'digital': DigitalMode,
        'ghost': GhostMode,
        'pitch': PitchMode,
        'revpitch': RevPitchMode,
    }
    
    # Style classes
    STYLE_CLASSES = {
        'single': SingleStyle,
        'dual': DualStyle,
        'ratio': RatioStyle,
        'pingpong': PingPongStyle,
        'quad': QuadStyle,
    }
    
    # Default parameters
    DEFAULT_PARAMS: Dict[str, Any] = {
        'mode': 'tape',
        'style': 'single',
        'mix': 0.5,
        'feedback': 0.5,
        'delay_time_ms': 500.0,
        'delay_time_l_ms': 500.0,
        'delay_time_r_ms': 500.0,
        'ratio': 0.5,
        'spread': 0.5,
        'mod_rate': 0.5,
        'mod_depth': 0.1,
        'age': 0.0,
        'drive': 0.0,
        'diffusion': 0.5,
        'diffusion_size': 0.5,
        'eq_high': 10000.0,
        'eq_low': 200.0,
        'era': 0.5,
        'ducking': 0.0,
        'pitch_shift': 0.0,
        'pitch_detune': 0.0,
        'frequency_shift': 0.0,
    }
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize the delay processor.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        
        # Create mode and style instances
        self.mode = self._create_mode(self.DEFAULT_PARAMS['mode'])
        self.style = self._create_style(self.DEFAULT_PARAMS['style'])
        
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
        
        # EQ filters
        self.eq_high = OnePoleFilter(
            cutoff_hz=10000.0,
            sample_rate=sample_rate,
            filter_type='lowpass'
        )
        self.eq_low = OnePoleFilter(
            cutoff_hz=200.0,
            sample_rate=sample_rate,
            filter_type='highpass'
        )
        
        # Parameter smoothing
        self._create_smoothers()
        
        # Parameters
        self.params = self.DEFAULT_PARAMS.copy()
        
        # Internal state
        self._prev_input_l = 0.0
        self._prev_input_r = 0.0
    
    def _create_mode(self, mode_name: str):
        """Create a mode instance."""
        if mode_name not in self.MODE_CLASSES:
            raise ValueError(f"Unknown mode: {mode_name}. Available: {list(self.MODE_CLASSES.keys())}")
        return self.MODE_CLASSES[mode_name](self.sample_rate)
    
    def _create_style(self, style_name: str):
        """Create a style instance."""
        if style_name not in self.STYLE_CLASSES:
            raise ValueError(f"Unknown style: {style_name}. Available: {list(self.STYLE_CLASSES.keys())}")
        return self.STYLE_CLASSES[style_name](self.sample_rate)
    
    def _create_smoothers(self):
        """Create smoothed parameters for click-free automation."""
        smooth_time_ms = 10.0  # 10ms
        
        self.smoothers = {
            'mix': SmoothedParameter(0.5, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'feedback': SmoothedParameter(0.5, 0.0, 0.99, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'delay_time_ms': SmoothedParameter(500.0, 1.0, 5000.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'delay_time_l_ms': SmoothedParameter(500.0, 1.0, 5000.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'delay_time_r_ms': SmoothedParameter(500.0, 1.0, 5000.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'ratio': SmoothedParameter(0.5, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'spread': SmoothedParameter(0.5, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'mod_rate': SmoothedParameter(0.5, 0.1, 10.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'mod_depth': SmoothedParameter(0.1, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'age': SmoothedParameter(0.0, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'drive': SmoothedParameter(0.0, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'diffusion': SmoothedParameter(0.5, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'diffusion_size': SmoothedParameter(0.5, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'eq_high': SmoothedParameter(10000.0, 100.0, 20000.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'eq_low': SmoothedParameter(200.0, 20.0, 1000.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'era': SmoothedParameter(0.5, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'ducking': SmoothedParameter(0.0, 0.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'pitch_shift': SmoothedParameter(0.0, -12.0, 12.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'pitch_detune': SmoothedParameter(0.0, -12.0, 12.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
            'frequency_shift': SmoothedParameter(0.0, -1.0, 1.0, smoothing_time_ms=smooth_time_ms, sample_rate=self.sample_rate),
        }
    
    def reset(self):
        """Reset all internal state."""
        self.mode.reset()
        self.style.reset()
        self.input_highpass.reset()
        self.input_lowpass.reset()
        self.output_highpass.reset()
        self.output_lowpass.reset()
        self.eq_high.reset()
        self.eq_low.reset()
        
        for smoother in self.smoothers.values():
            smoother.reset()
        
        self._prev_input_l = 0.0
        self._prev_input_r = 0.0
    
    def set_sample_rate(self, sample_rate: int):
        """Set sample rate."""
        self.sample_rate = sample_rate
        self.mode.set_sample_rate(sample_rate)
        self.style.set_sample_rate(sample_rate)
        self.input_highpass.set_sample_rate(sample_rate)
        self.input_lowpass.set_sample_rate(sample_rate)
        self.output_highpass.set_sample_rate(sample_rate)
        self.output_lowpass.set_sample_rate(sample_rate)
        self.eq_high.set_sample_rate(sample_rate)
        self.eq_low.set_sample_rate(sample_rate)
        
        self._create_smoothers()
    
    def set_mode(self, mode_name: str):
        """
        Set the delay mode.
        
        Args:
            mode_name: Mode name (tape, hifi, bbd, digital, ghost, pitch, revpitch)
        """
        if mode_name not in self.MODE_CLASSES:
            raise ValueError(f"Unknown mode: {mode_name}")
        
        self.params['mode'] = mode_name
        self.mode = self._create_mode(mode_name)
    
    def set_style(self, style_name: str):
        """
        Set the delay style.
        
        Args:
            style_name: Style name (single, dual, ratio, pingpong, quad)
        """
        if style_name not in self.STYLE_CLASSES:
            raise ValueError(f"Unknown style: {style_name}")
        
        self.params['style'] = style_name
        self.style = self._create_style(style_name)
    
    def set_parameters(self, params: Dict[str, Any]):
        """
        Set all parameters at once.
        
        Args:
            params: Dictionary of parameter name -> value
        """
        for key, value in params.items():
            if key in self.params:
                self.params[key] = value
        
        # Update mode parameters (mode has params dict, not DEFAULT_PARAMS)
        mode_params = {k: v for k, v in params.items() if k in self.mode.params}
        if mode_params:
            for key, value in mode_params.items():
                if hasattr(self.mode, 'set_' + key):
                    getattr(self.mode, 'set_' + key)(value)
                else:
                    self.mode.params[key] = value
        
        # Update style parameters
        style_params = {k: v for k, v in params.items() if k in self.style.params}
        if style_params:
            for key, value in style_params.items():
                if hasattr(self.style, 'set_' + key):
                    getattr(self.style, 'set_' + key)(value)
                else:
                    self.style.params[key] = value
        
        # Update mode if changed
        if 'mode' in params:
            self.set_mode(params['mode'])
        
        # Update style if changed
        if 'style' in params:
            self.set_style(params['style'])
        
        # Update filters
        if 'eq_high' in params:
            self.eq_high.set_cutoff(params['eq_high'])
        if 'eq_low' in params:
            self.eq_low.set_cutoff(params['eq_low'])
    
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
        1. Input filtering
        2. Mode processing
        3. Style routing
        4. Output filtering
        5. Dry/wet mix
        
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
        
        # Get delay time from smoothed parameters
        delay_time_ms = smoothed.get('delay_time_ms', 500.0)
        
        # Process through mode
        mode_l, mode_r = self.mode.process_sample(input_l_filtered, input_r_filtered)
        
        # Process through style
        style_l, style_r = self.style.process(mode_l, mode_r, delay_time_ms)
        
        # Apply EQ
        eq_high = smoothed.get('eq_high', 10000.0)
        eq_low = smoothed.get('eq_low', 200.0)
        
        # Simple EQ: just apply filters for now
        output_l = self.eq_low.process(style_l)
        output_l = self.eq_high.process(output_l)
        output_r = self.eq_low.process(style_r)
        output_r = self.eq_high.process(output_r)
        
        # Apply output filtering
        output_l = self.output_highpass.process(output_l)
        output_l = self.output_lowpass.process(output_l)
        output_r = self.output_highpass.process(output_r)
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
    
    def get_impulse_response(self, duration_seconds: float = 1.0) -> np.ndarray:
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
        return list(self.MODE_CLASSES.keys())
    
    def list_styles(self) -> list:
        """List all available styles."""
        return list(self.STYLE_CLASSES.keys())


# Test
if __name__ == "__main__":
    print("Testing DelayProcessor...")
    
    # Create processor
    processor = DelayProcessor(sample_rate=44100)
    
    # Test with different modes and styles
    for mode in ['tape', 'hifi', 'digital', 'bbd']:
        for style in ['single', 'pingpong']:
            print(f"\nMode: {mode}, Style: {style}")
            processor.set_mode(mode)
            processor.set_style(style)
            
            # Set some parameters
            processor.set_parameters({
                'mix': 1.0,
                'delay_time_ms': 500.0,
                'feedback': 0.5,
            })
            
            # Generate impulse response
            ir = processor.get_impulse_response(duration_seconds=0.5)
            print(f'  IR shape: {ir.shape}')
            print(f'  IR peak: {np.max(np.abs(ir)):.6f}')
    
    print('\nDelayProcessor test completed successfully!')
