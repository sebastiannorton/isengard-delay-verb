# Reference Rendering Framework
# For rendering reference plugin outputs

"""
Reference rendering framework for Isengard plugin testing.

Features:
- Render reference plugin outputs with specified configurations
- Save outputs with metadata
- Support for various signal types
- Integration with analysis tools

Usage:
    from reference_rendering.render import ReferenceRenderer
    
    # Create renderer
    renderer = ReferenceRenderer(output_dir='outputs')
    
    # Render with configuration file
    renderer.render_from_config('tests/reference_rendering/configs/delay-modes/tape-single-impulse.json')
    
    # Render with explicit parameters
    renderer.render(
        plugin='delay',
        mode='Tape',
        style='Single',
        params={'feedback': 0.5, 'delayTimeMs': 500},
        signal_generator=impulse_gen,
        sample_rate=44100
    )
"""

import json
import numpy as np
import os
from datetime import datetime
import soundfile as sf


class ReferenceRenderer:
    """
    Render reference plugin outputs for testing.
    
    This class handles the rendering of reference outputs using the
    actual reference plugins (when available) or mock plugins for
    testing the framework.
    
    Parameters:
        output_dir (str): Directory to save outputs (default: 'outputs')
    """
    
    def __init__(self, output_dir='outputs'):
        """
        Initialize the reference renderer.
        
        Args:
            output_dir: Directory to save outputs
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def render_from_config(self, config_file):
        """
        Render using a configuration file.
        
        Args:
            config_file: Path to JSON configuration file
            
        Returns:
            dict: Rendering results
        """
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        return self.render(**config)
    
    def render(self, plugin, mode=None, style=None, color=None, params=None,
               signal=None, signal_type='impulse', sample_rate=44100,
               duration_seconds=5.0, block_size=1024, name=None, notes=None):
        """
        Render a reference output.
        
        Args:
            plugin: Plugin type ('delay' or 'verb')
            mode: Mode for the plugin
            style: Style for delay plugin
            color: Color for verb plugin
            params: Dictionary of parameter values
            signal: Pre-generated signal (optional)
            signal_type: Type of signal to generate if signal is None
            sample_rate: Sample rate in Hz
            duration_seconds: Duration of the rendering in seconds
            block_size: Block size for processing
            name: Name for this rendering
            notes: Notes about this rendering
            
        Returns:
            dict: Rendering results
        """
        # Create output directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate directory name
        dir_name_parts = [plugin]
        if mode:
            dir_name_parts.append(mode)
        if style:
            dir_name_parts.append(style)
        if color:
            dir_name_parts.append(color)
        dir_name_parts.append(timestamp)
        
        render_dir = os.path.join(self.output_dir, '_'.join(dir_name_parts))
        os.makedirs(render_dir, exist_ok=True)
        
        # Generate signal if not provided
        if signal is None:
            signal = self._generate_signal(signal_type, sample_rate, duration_seconds)
        
        # Process through reference plugin (placeholder)
        # In practice, this would use the actual reference plugin
        output = self._process_reference(
            signal, plugin, mode, style, color, params, sample_rate, block_size
        )
        
        # Save output
        output_file = os.path.join(render_dir, 'output.wav')
        self._save_output(output, output_file, sample_rate)
        
        # Analyze output
        analysis = self._analyze_output(output, sample_rate)
        
        # Save metadata
        metadata = {
            'plugin': plugin,
            'mode': mode,
            'style': style,
            'color': color,
            'params': params or {},
            'signal_type': signal_type,
            'sample_rate': sample_rate,
            'duration_seconds': duration_seconds,
            'block_size': block_size,
            'name': name,
            'notes': notes,
            'timestamp': timestamp,
            'output_file': 'output.wav',
            'analysis': analysis
        }
        
        with open(os.path.join(render_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            'directory': render_dir,
            'output_file': output_file,
            'analysis': analysis,
            'metadata': metadata
        }
    
    def _generate_signal(self, signal_type, sample_rate, duration_seconds):
        """
        Generate a test signal.
        
        Args:
            signal_type: Type of signal ('impulse', 'white', 'pink', 'sine')
            sample_rate: Sample rate in Hz
            duration_seconds: Duration in seconds
            
        Returns:
            numpy.ndarray: Generated signal
        """
        length_samples = int(duration_seconds * sample_rate)
        
        if signal_type == 'impulse':
            signal = np.zeros(length_samples, dtype=np.float32)
            signal[0] = 0.5
            return signal
        
        elif signal_type == 'white':
            return np.random.uniform(-0.5, 0.5, length_samples).astype(np.float32)
        
        elif signal_type == 'pink':
            # Simple pink noise approximation
            white = np.random.uniform(-0.5, 0.5, length_samples)
            # Apply a simple lowpass filter
            b, a = [0.049922035], [1, -0.950077965]
            for i in range(1, length_samples):
                white[i] = b[0] * white[i] + a[1] * white[i-1]
            return white.astype(np.float32)
        
        elif signal_type == 'sine':
            t = np.arange(length_samples, dtype=np.float32) / sample_rate
            return (0.5 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)
        
        else:
            raise ValueError(f"Unknown signal type: {signal_type}")
    
    def _process_reference(self, signal, plugin, mode, style, color, params, sample_rate, block_size):
        """
        Process signal through reference plugin.
        
        This is a placeholder. In practice, this would use the actual
        reference plugin (ValhallaDelay or ValhallaVintageVerb).
        
        Args:
            signal: Input signal
            plugin: Plugin type
            mode: Mode
            style: Style
            color: Color
            params: Parameters
            sample_rate: Sample rate
            block_size: Block size
            
        Returns:
            numpy.ndarray: Processed signal
        """
        # For now, just return the input signal
        # This would be replaced with actual plugin processing
        print(f"  Note: Using mock reference processing for {plugin} mode={mode}")
        return signal
    
    def _save_output(self, signal, filename, sample_rate):
        """
        Save output signal as WAV file.
        
        Args:
            signal: Signal to save
            filename: Output filename
            sample_rate: Sample rate
        """
        # Ensure signal is float32
        signal = signal.astype(np.float32)
        
        # Write WAV file using soundfile
        sf.write(filename, signal, sample_rate, subtype='FLOAT', format='WAV')
        
        # Log
        print(f"  Output saved as WAV: {filename}")
    
    def _analyze_output(self, signal, sample_rate):
        """
        Analyze output signal.
        
        Args:
            signal: Output signal
            sample_rate: Sample rate
            
        Returns:
            dict: Analysis results
        """
        # Compute basic metrics
        rms = float(np.sqrt(np.mean(signal ** 2)))
        peak = float(np.max(np.abs(signal)))
        
        # Compute FFT
        nfft = min(4096, len(signal))
        fft_result = np.fft.rfft(signal, n=nfft)
        fft_mag = np.abs(fft_result)
        fft_phase = np.angle(fft_result)
        fft_freq = np.fft.rfftfreq(nfft, 1.0 / sample_rate)
        
        # Compute spectral metrics
        spectral_centroid = self._compute_spectral_centroid(fft_freq, fft_mag)
        spectral_flatness = self._compute_spectral_flatness(fft_mag)
        
        return {
            'rms': rms,
            'peak': peak,
            'fft_frequencies': fft_freq.tolist(),
            'fft_magnitude': fft_mag.tolist(),
            'fft_phase': fft_phase.tolist(),
            'spectral_centroid': spectral_centroid,
            'spectral_flatness': spectral_flatness
        }
    
    def _compute_spectral_centroid(self, frequencies, magnitude):
        """Compute spectral centroid."""
        if np.sum(magnitude) > 0:
            return float(np.sum(frequencies * magnitude) / np.sum(magnitude))
        return 0.0
    
    def _compute_spectral_flatness(self, magnitude):
        """Compute spectral flatness."""
        epsilon = 1e-10
        magnitude = magnitude + epsilon
        
        # Skip DC component
        magnitude = magnitude[1:]
        
        if len(magnitude) == 0:
            return 0.0
        
        am = np.mean(magnitude)
        gm = np.exp(np.mean(np.log(magnitude)))
        
        return float(gm / (am + epsilon))


# Example usage
if __name__ == "__main__":
    import json
    
    print("Reference Rendering Framework Example")
    print("=" * 50)
    
    # Create renderer
    renderer = ReferenceRenderer(output_dir='test_render_outputs')
    
    # Render with explicit parameters
    print("\nRendering with explicit parameters:")
    result = renderer.render(
        plugin='delay',
        mode='Tape',
        style='Single',
        params={'feedback': 0.5, 'delayTimeMs': 500},
        signal_type='impulse',
        sample_rate=44100,
        duration_seconds=3.0,
        name='Tape Single Impulse',
        notes='Test rendering for Tape mode with Single style'
    )
    
    print(f"\nRendering completed!")
    print(f"  Output directory: {result['directory']}")
    print(f"  Output file: {result['output_file']}")
    print(f"  RMS: {result['analysis']['rms']:.6f}")
    print(f"  Peak: {result['analysis']['peak']:.6f}")
    print(f"  Spectral centroid: {result['analysis']['spectral_centroid']:.1f} Hz")
    
    # Render with configuration file
    print("\nRendering with configuration file:")
    result = renderer.render_from_config(
        'tests/reference_rendering/configs/delay-modes/tape-single-impulse.json'
    )
    
    print(f"\nRendering completed!")
    print(f"  Output directory: {result['directory']}")
    print(f"  Metadata saved to: {result['directory']}/metadata.json")
    
    print("\nNote: This is a demonstration with mock reference processing.")
    print("In practice, you would use the actual reference plugins.")
