# Parameter Sweep Framework
# For automated parameter testing

"""
Parameter sweep framework for automated testing of Isengard plugins.

Features:
- Automated parameter sweeps
- Support for linear and logarithmic parameter ranges
- JSON-based configuration
- Result saving and analysis
- Integration with signal generators and analyzers

Usage:
    from parameter_sweeps.sweep import ParameterSweep
    
    # Create sweep
    sweep = ParameterSweep(config_file='parameter-sweeps/definitions/delay-params.json')
    
    # Run sweep for a specific parameter
    results = sweep.run_sweep(
        plugin='delay',
        param_name='feedback',
        mode='Tape',
        style='Single',
        signal_generator=impulse_gen,
        processor=delay_processor
    )
"""

import json
import numpy as np
import os
from datetime import datetime


class ParameterSweep:
    """
    Framework for running automated parameter sweeps.
    
    This class handles the configuration, execution, and result saving
    for parameter sweeps across the Isengard plugins.
    
    Parameters:
        config_file (str): Path to JSON configuration file
        output_dir (str): Directory to save results (default: 'results')
    """
    
    def __init__(self, config_file, output_dir='results'):
        """
        Initialize the parameter sweep framework.
        
        Args:
            config_file: Path to JSON configuration file
            output_dir: Directory to save results
        """
        self.config_file = config_file
        self.output_dir = output_dir
        self.config = None
        self.load_config()
    
    def load_config(self):
        """Load the configuration from the JSON file."""
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
    
    def get_parameter_info(self, param_name):
        """
        Get information about a specific parameter.
        
        Args:
            param_name: Name of the parameter
            
        Returns:
            dict: Parameter configuration
        """
        for param in self.config.get('parameters', []):
            if param['name'] == param_name:
                return param
        return None
    
    def generate_sweep_values(self, param_name, num_steps=None):
        """
        Generate values for a parameter sweep.
        
        Args:
            param_name: Name of the parameter
            num_steps: Number of steps (default: use parameter's steps)
            
        Returns:
            numpy.ndarray: Array of parameter values
        """
        param = self.get_parameter_info(param_name)
        if param is None:
            raise ValueError(f"Parameter {param_name} not found in configuration")
        
        if num_steps is None:
            num_steps = param.get('steps', 10)
        
        param_range = param['range']
        param_type = param.get('type', 'linear')
        
        if param_type == 'linear':
            return np.linspace(param_range[0], param_range[1], num_steps)
        elif param_type == 'logarithmic':
            return np.logspace(
                np.log10(param_range[0]),
                np.log10(param_range[1]),
                num_steps
            )
        else:
            # Default to linear
            return np.linspace(param_range[0], param_range[1], num_steps)
    
    def run_sweep(self, plugin, param_name, signal_generator, processor,
                  mode=None, style=None, color=None, output_dir=None):
        """
        Run a parameter sweep.
        
        Args:
            plugin: Plugin type ('delay' or 'verb')
            param_name: Name of the parameter to sweep
            signal_generator: Signal generator instance
            processor: Plugin processor instance
            mode: Mode for the plugin (default: None)
            style: Style for delay plugin (default: None)
            color: Color for verb plugin (default: None)
            output_dir: Override output directory (default: None)
            
        Returns:
            dict: Sweep results
        """
        # Get parameter info
        param = self.get_parameter_info(param_name)
        if param is None:
            raise ValueError(f"Parameter {param_name} not found in configuration")
        
        # Generate sweep values
        values = self.generate_sweep_values(param_name)
        
        # Create output directory
        if output_dir is None:
            output_dir = self.output_dir
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sweep_dir = os.path.join(
            output_dir,
            f"{plugin}_{param_name}"
            f"{'_' + mode if mode else ''}"
            f"{'_' + style if style else ''}"
            f"{'_' + color if color else ''}"
            f"_{timestamp}"
        )
        os.makedirs(sweep_dir, exist_ok=True)
        
        # Save configuration
        config = {
            'plugin': plugin,
            'param': param_name,
            'mode': mode,
            'style': style,
            'color': color,
            'timestamp': timestamp,
            'signal': signal_generator.__class__.__name__,
            'num_steps': len(values),
            'param_range': param['range'],
            'param_type': param.get('type', 'linear')
        }
        with open(os.path.join(sweep_dir, 'config.json'), 'w') as f:
            json.dump(config, f, indent=2)
        
        # Run sweep
        results = []
        for i, value in enumerate(values):
            # Set parameter
            if plugin == 'delay':
                if mode:
                    processor.set_mode(mode)
                if style:
                    processor.set_style(style)
                processor.set_parameter(param_name, value)
            elif plugin == 'verb':
                if mode:
                    processor.set_mode(mode)
                if color:
                    processor.set_color(color)
                processor.set_parameter(param_name, value)
            
            # Generate test signal
            signal = signal_generator.generate()
            
            # Process signal
            output = processor.process(signal)
            
            # Save output
            output_file = os.path.join(sweep_dir, f"{param_name}_{value:.6f}.wav")
            self._save_wav(output, output_file, signal_generator.sample_rate)
            
            # Analyze output
            analysis = self._analyze_output(output, signal_generator.sample_rate)
            
            results.append({
                'index': i,
                'value': float(value),
                'output_file': output_file,
                'analysis': analysis
            })
            
            print(f"  [{i+1}/{len(values)}] {param_name}={value:.4f} -> {output_file}")
        
        # Save results
        with open(os.path.join(sweep_dir, 'results.json'), 'w') as f:
            json.dump(results, f, indent=2)
        
        return {
            'config': config,
            'results': results,
            'directory': sweep_dir
        }
    
    def run_full_sweep(self, plugin, signal_generator, processor,
                       modes=None, styles=None, colors=None,
                       params=None, output_dir=None):
        """
        Run a full parameter sweep across all parameters and configurations.
        
        Args:
            plugin: Plugin type ('delay' or 'verb')
            signal_generator: Signal generator instance
            processor: Plugin processor instance
            modes: List of modes to test (default: all modes from config)
            styles: List of styles to test (default: all styles from config)
            colors: List of colors to test (default: all colors from config)
            params: List of parameters to sweep (default: all parameters from config)
            output_dir: Override output directory (default: None)
            
        Returns:
            list: List of sweep results for each parameter/configuration
        """
        # Get configurations from config
        if modes is None:
            modes = [m['name'] for m in self.config.get('modes', [])]
        if styles is None:
            styles = [s['name'] for s in self.config.get('styles', [])]
        if colors is None:
            colors = [c['name'] for c in self.config.get('colors', [])]
        if params is None:
            params = [p['name'] for p in self.config.get('parameters', [])]
        
        all_results = []
        
        # For delay plugin, iterate over modes and styles
        if plugin == 'delay':
            for mode in modes:
                for style in styles:
                    for param in params:
                        print(f"\nSweeping {param} for mode={mode}, style={style}")
                        result = self.run_sweep(
                            plugin=plugin,
                            param_name=param,
                            signal_generator=signal_generator,
                            processor=processor,
                            mode=mode,
                            style=style,
                            output_dir=output_dir
                        )
                        all_results.append(result)
        
        # For verb plugin, iterate over modes and colors
        elif plugin == 'verb':
            for mode in modes:
                for color in colors:
                    for param in params:
                        print(f"\nSweeping {param} for mode={mode}, color={color}")
                        result = self.run_sweep(
                            plugin=plugin,
                            param_name=param,
                            signal_generator=signal_generator,
                            processor=processor,
                            mode=mode,
                            color=color,
                            output_dir=output_dir
                        )
                        all_results.append(result)
        
        return all_results
    
    def _analyze_output(self, signal, sample_rate):
        """
        Analyze an output signal.
        
        Args:
            signal: Output signal
            sample_rate: Sample rate in Hz
            
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
        
        return {
            'rms': rms,
            'peak': peak,
            'fft_frequencies': fft_freq.tolist(),
            'fft_magnitude': fft_mag.tolist(),
            'fft_phase': fft_phase.tolist()
        }
    
    def _save_wav(self, signal, filename, sample_rate):
        """
        Save a signal as a WAV file.
        
        Args:
            signal: Signal to save
            filename: Output filename
            sample_rate: Sample rate in Hz
        """
        # This is a placeholder - in practice, use scipy.io.wavfile or soundfile
        # For now, just save as numpy array
        np.save(filename.replace('.wav', '.npy'), signal)
        
        # Log that we're saving as numpy array
        print(f"  Note: Saving as numpy array ({filename.replace('.wav', '.npy')})")
        print(f"  To save as WAV, install scipy or soundfile")


# Example usage (requires plugin implementation)
if __name__ == "__main__":
    import json
    import numpy as np
    from signals.impulse import ImpulseGenerator
    
    print("Parameter Sweep Framework Example")
    print("=" * 50)
    
    # Create a mock plugin processor for demonstration
    class MockDelayProcessor:
        def __init__(self):
            self.params = {}
            self.mode = None
            self.style = None
            
        def set_mode(self, mode):
            self.mode = mode
            
        def set_style(self, style):
            self.style = style
            
        def set_parameter(self, name, value):
            self.params[name] = value
            
        def process(self, signal):
            # Simple processing: apply gain based on feedback parameter
            feedback = self.params.get('feedback', 0.0)
            # Simple delay simulation: just return the signal with some modification
            # In practice, this would be the actual plugin processing
            return signal * (1.0 - feedback * 0.5)
    
    # Create sweep framework
    # First, create a simple config for demonstration
    config = {
        "parameters": [
            {
                "name": "feedback",
                "display_name": "Feedback",
                "range": [0.0, 0.99],
                "type": "logarithmic",
                "steps": 10,
                "unit": "",
                "description": "Feedback amount"
            },
            {
                "name": "delayTimeMs",
                "display_name": "Delay Time",
                "range": [1.0, 5000.0],
                "type": "logarithmic",
                "steps": 10,
                "unit": "ms",
                "description": "Delay time in milliseconds"
            }
        ],
        "modes": [
            {"name": "Tape", "display_name": "Tape"},
            {"name": "HiFi", "display_name": "HiFi"}
        ],
        "styles": [
            {"name": "Single", "display_name": "Single"},
            {"name": "PingPong", "display_name": "PingPong"}
        ]
    }
    
    # Save config to temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f, indent=2)
        config_file = f.name
    
    try:
        # Create sweep
        sweep = ParameterSweep(config_file, output_dir='test_sweep_results')
        
        # Create signal generator
        signal_gen = ImpulseGenerator(sample_rate=44100, length_samples=44100)
        
        # Create mock processor
        processor = MockDelayProcessor()
        
        # Run sweep for feedback parameter
        print("\nRunning sweep for feedback parameter:")
        result = sweep.run_sweep(
            plugin='delay',
            param_name='feedback',
            signal_generator=signal_gen,
            processor=processor,
            mode='Tape',
            style='Single'
        )
        
        print(f"\nSweep completed!")
        print(f"  Results saved to: {result['directory']}")
        print(f"  Number of steps: {len(result['results'])}")
        
        # Show first few results
        print(f"\nFirst 3 results:")
        for r in result['results'][:3]:
            print(f"  Value: {r['value']:.4f}, RMS: {r['analysis']['rms']:.6f}, Peak: {r['analysis']['peak']:.6f}")
        
    finally:
        # Clean up temporary file
        import os
        os.unlink(config_file)
    
    print("\nNote: This is a demonstration with a mock processor.")
    print("In practice, you would use the actual Isengard plugin processors.")
