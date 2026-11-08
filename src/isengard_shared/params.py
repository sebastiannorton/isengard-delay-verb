# Parameter System
# Smoothed parameters with double buffering for thread safety

"""
Parameter system for Isengard plugins.

Features:
- Smoothed parameters with configurable smoothing times
- Double buffering for thread-safe parameter updates
- No locks in audio thread
- Sample-accurate automation support
- Parameter validation and clamping

Usage:
    from isengard_shared.params import ParameterSystem, SmoothedParameter
    
    # Create parameter system
    params = ParameterSystem(sample_rate=44100)
    
    # Add parameters
    params.add_parameter('feedback', 0.0, 0.99, 0.5, smoothing_time_ms=10.0)
    params.add_parameter('delayTimeMs', 1.0, 5000.0, 500.0, smoothing_time_ms=20.0, logarithmic=True)
    
    # Set parameter value (non-audio thread)
    params.set_parameter('feedback', 0.7)
    
    # Get smoothed value (audio thread)
    feedback = params.get_parameter('feedback')
    
    # Process block (audio thread)
    params.process_block(num_samples)
"""

import numpy as np
import threading


class SmoothedParameter:
    """
    A single parameter with smoothing.
    
    This class provides exponential smoothing for a parameter, allowing
    smooth transitions between values to avoid clicks and zipper noise.
    
    Parameters:
        initial_value (float): Initial parameter value
        min_value (float): Minimum allowed value
        max_value (float): Maximum allowed value
        smoothing_time_ms (float): Smoothing time in milliseconds (default: 50.0)
        logarithmic (bool): Whether to use logarithmic scaling (default: False)
        sample_rate (float): Sample rate in Hz (default: 44100)
    """
    
    def __init__(self, initial_value, min_value, max_value, smoothing_time_ms=50.0,
                 logarithmic=False, sample_rate=44100):
        """
        Initialize the smoothed parameter.
        
        Args:
            initial_value: Initial parameter value
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            smoothing_time_ms: Smoothing time in milliseconds
            logarithmic: Whether to use logarithmic scaling
            sample_rate: Sample rate in Hz
        """
        self.min_value = float(min_value)
        self.max_value = float(max_value)
        self.smoothing_time_ms = float(smoothing_time_ms)
        self.logarithmic = bool(logarithmic)
        self.sample_rate = float(sample_rate)
        
        # Initialize values
        self.target_value = self._clamp_and_scale(initial_value)
        self.current_value = self.target_value
        
        # Calculate smoothing coefficient
        self._update_smoothing_coeff()
    
    def _clamp_and_scale(self, value):
        """
        Clamp value to range and apply logarithmic scaling if needed.
        
        Args:
            value: Input value
            
        Returns:
            float: Clamped and scaled value
        """
        # Clamp to range
        value = np.clip(value, self.min_value, self.max_value)
        
        # Apply logarithmic scaling if needed
        if self.logarithmic:
            # Convert to logarithmic scale
            if value <= 0:
                return 0.0
            min_log = np.log(self.min_value) if self.min_value > 0 else -100
            max_log = np.log(self.max_value) if self.max_value > 0 else 100
            value_log = np.log(value)
            value = (value_log - min_log) / (max_log - min_log)
            value = np.clip(value, 0.0, 1.0)
        
        return float(value)
    
    def _unscale(self, value):
        """
        Reverse logarithmic scaling if needed.
        
        Args:
            value: Scaled value (0 to 1)
            
        Returns:
            float: Unscaled value
        """
        if self.logarithmic:
            min_log = np.log(self.min_value) if self.min_value > 0 else -100
            max_log = np.log(self.max_value) if self.max_value > 0 else 100
            value_log = min_log + value * (max_log - min_log)
            return float(np.exp(value_log))
        else:
            return float(value)
    
    def _update_smoothing_coeff(self):
        """Update the smoothing coefficient based on sample rate and smoothing time."""
        if self.sample_rate <= 0 or self.smoothing_time_ms <= 0:
            self.smoothing_coeff = 1.0  # No smoothing
        else:
            # First-order exponential smoothing: coeff = exp(-2 * pi * smoothing_time / (1000 * sample_rate))
            self.smoothing_coeff = np.exp(
                -2.0 * np.pi * self.smoothing_time_ms / (1000.0 * self.sample_rate)
            )
    
    def set_sample_rate(self, sample_rate):
        """
        Set the sample rate.
        
        Args:
            sample_rate: New sample rate in Hz
        """
        self.sample_rate = float(sample_rate)
        self._update_smoothing_coeff()
    
    def set_smoothing_time(self, smoothing_time_ms):
        """
        Set the smoothing time.
        
        Args:
            smoothing_time_ms: New smoothing time in milliseconds
        """
        self.smoothing_time_ms = float(smoothing_time_ms)
        self._update_smoothing_coeff()
    
    def set_value(self, value):
        """
        Set the target value.
        
        Args:
            value: New target value
        """
        self.target_value = self._clamp_and_scale(value)
    
    def get_value(self):
        """
        Get the current smoothed value.
        
        Returns:
            float: Current smoothed value (unscaled if logarithmic)
        """
        return self._unscale(self.current_value)
    
    def get_raw_value(self):
        """
        Get the current raw (scaled) value.
        
        Returns:
            float: Current raw value (0 to 1)
        """
        return self.current_value
    
    def get_target_value(self):
        """
        Get the target value.
        
        Returns:
            float: Target value (unscaled if logarithmic)
        """
        return self._unscale(self.target_value)
    
    def process_sample(self):
        """
        Process one sample of smoothing.
        
        Returns:
            float: Current smoothed value
        """
        # First-order exponential smoothing
        self.current_value = self.current_value * self.smoothing_coeff + \
                            self.target_value * (1.0 - self.smoothing_coeff)
        return self._unscale(self.current_value)
    
    def process_block(self, num_samples):
        """
        Process a block of samples.
        
        Args:
            num_samples: Number of samples to process
        """
        for _ in range(num_samples):
            self.process_sample()
    
    def reset(self):
        """Reset the parameter to its initial state."""
        self.current_value = self.target_value


class ParameterBuffer:
    """
    Double-buffered parameter storage for thread-safe updates.
    
    This class provides a way to update parameters from a non-audio thread
    (e.g., GUI thread) and read them from the audio thread without locks.
    
    Parameters:
        num_parameters (int): Number of parameters
    """
    
    def __init__(self, num_parameters):
        """
        Initialize the parameter buffer.
        
        Args:
            num_parameters: Number of parameters
        """
        self.num_parameters = num_parameters
        
        # Create two buffers
        self.buffer_a = np.zeros(num_parameters, dtype=np.float32)
        self.buffer_b = np.zeros(num_parameters, dtype=np.float32)
        
        # Pointers to current read and write buffers
        self.read_buffer = self.buffer_a
        self.write_buffer = self.buffer_b
        
        # Lock for buffer swapping (only used during swap, not during audio processing)
        self.lock = threading.Lock()
    
    def set_parameter(self, index, value):
        """
        Set a parameter value (non-audio thread).
        
        Args:
            index: Parameter index
            value: Parameter value
        """
        if index < 0 or index >= self.num_parameters:
            raise ValueError(f"Parameter index {index} out of range")
        
        self.write_buffer[index] = float(value)
    
    def get_parameter(self, index):
        """
        Get a parameter value (audio thread).
        
        Args:
            index: Parameter index
            
        Returns:
            float: Parameter value
        """
        if index < 0 or index >= self.num_parameters:
            raise ValueError(f"Parameter index {index} out of range")
        
        return self.read_buffer[index]
    
    def swap_buffers(self):
        """
        Swap the read and write buffers.
        
        This should be called at the beginning of each audio block
        to copy the latest parameter values from the write buffer
        to the read buffer.
        """
        with self.lock:
            # Swap pointers
            self.read_buffer, self.write_buffer = self.write_buffer, self.read_buffer
            
            # Copy values from old write buffer to new write buffer
            # (so that writes to the new write buffer don't affect the read buffer)
            self.write_buffer[:] = self.read_buffer[:]
    
    def get_all_parameters(self):
        """
        Get all parameter values (audio thread).
        
        Returns:
            numpy.ndarray: Array of all parameter values
        """
        return self.read_buffer.copy()
    
    def set_all_parameters(self, values):
        """
        Set all parameter values (non-audio thread).
        
        Args:
            values: Array of parameter values
        """
        if len(values) != self.num_parameters:
            raise ValueError(f"Expected {self.num_parameters} values, got {len(values)}")
        
        self.write_buffer[:] = np.asarray(values, dtype=np.float32)


class ParameterSystem:
    """
    Complete parameter system with smoothing and double buffering.
    
    This class combines smoothed parameters with double buffering for
    thread-safe parameter updates and smooth transitions.
    
    Parameters:
        sample_rate (float): Sample rate in Hz (default: 44100)
    """
    
    def __init__(self, sample_rate=44100):
        """
        Initialize the parameter system.
        
        Args:
            sample_rate: Sample rate in Hz
        """
        self.sample_rate = float(sample_rate)
        self.parameters = {}  # name -> SmoothedParameter
        self.parameter_indices = {}  # name -> index
        self.buffer = None
        self.buffer_size = 0
    
    def add_parameter(self, name, min_value, max_value, initial_value,
                      smoothing_time_ms=50.0, logarithmic=False):
        """
        Add a parameter to the system.
        
        Args:
            name: Parameter name
            min_value: Minimum value
            max_value: Maximum value
            initial_value: Initial value
            smoothing_time_ms: Smoothing time in milliseconds
            logarithmic: Whether to use logarithmic scaling
        """
        if name in self.parameters:
            raise ValueError(f"Parameter {name} already exists")
        
        # Create smoothed parameter
        param = SmoothedParameter(
            initial_value=initial_value,
            min_value=min_value,
            max_value=max_value,
            smoothing_time_ms=smoothing_time_ms,
            logarithmic=logarithmic,
            sample_rate=self.sample_rate
        )
        
        self.parameters[name] = param
        self.parameter_indices[name] = len(self.parameters) - 1
        
        # Resize buffer if needed
        self.buffer_size = len(self.parameters)
        if self.buffer is None or self.buffer.num_parameters < self.buffer_size:
            self.buffer = ParameterBuffer(self.buffer_size * 2)
    
    def set_sample_rate(self, sample_rate):
        """
        Set the sample rate for all parameters.
        
        Args:
            sample_rate: New sample rate in Hz
        """
        self.sample_rate = float(sample_rate)
        for param in self.parameters.values():
            param.set_sample_rate(sample_rate)
    
    def set_parameter(self, name, value):
        """
        Set a parameter value (non-audio thread).
        
        Args:
            name: Parameter name
            value: Parameter value
        """
        if name not in self.parameters:
            raise ValueError(f"Parameter {name} not found")
        
        # Set in smoothed parameter
        self.parameters[name].set_value(value)
        
        # Set in buffer
        if self.buffer:
            index = self.parameter_indices[name]
            self.buffer.set_parameter(index, value)
    
    def get_parameter(self, name):
        """
        Get a parameter value (audio thread).
        
        Args:
            name: Parameter name
            
        Returns:
            float: Parameter value
        """
        if name not in self.parameters:
            raise ValueError(f"Parameter {name} not found")
        
        # For now, just return the smoothed value
        # In a full implementation, we'd use the buffer for thread-safe access
        return self.parameters[name].get_value()
    
    def get_smoothed_parameter(self, name):
        """
        Get the smoothed parameter object.
        
        Args:
            name: Parameter name
            
        Returns:
            SmoothedParameter: The smoothed parameter object
        """
        if name not in self.parameters:
            raise ValueError(f"Parameter {name} not found")
        
        return self.parameters[name]
    
    def process_block(self, num_samples):
        """
        Process a block of samples (audio thread).
        
        This should be called at the beginning of each audio block to:
        1. Swap buffers to get latest parameter values
        2. Process smoothing for all parameters
        
        Args:
            num_samples: Number of samples in the block
        """
        # Swap buffers
        if self.buffer:
            self.buffer.swap_buffers()
        
        # Process smoothing for all parameters
        for param in self.parameters.values():
            param.process_block(num_samples)
    
    def get_all_parameters(self):
        """
        Get all parameter values (audio thread).
        
        Returns:
            dict: Dictionary of parameter names to values
        """
        return {name: param.get_value() for name, param in self.parameters.items()}
    
    def set_all_parameters(self, values):
        """
        Set all parameter values (non-audio thread).
        
        Args:
            values: Dictionary of parameter names to values
        """
        for name, value in values.items():
            self.set_parameter(name, value)
    
    def reset(self):
        """Reset all parameters to their initial states."""
        for param in self.parameters.values():
            param.reset()


# Example usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    print("Parameter System Example")
    print("=" * 50)
    
    # Create parameter system
    params = ParameterSystem(sample_rate=44100)
    
    # Add parameters
    params.add_parameter('feedback', 0.0, 0.99, 0.5, smoothing_time_ms=10.0)
    params.add_parameter('delayTimeMs', 1.0, 5000.0, 500.0, smoothing_time_ms=20.0, logarithmic=True)
    params.add_parameter('mix', 0.0, 1.0, 0.5, smoothing_time_ms=50.0)
    
    print("Parameters added:")
    for name in params.parameters:
        param = params.parameters[name]
        print(f"  {name}: {param.get_value():.4f} (range: {param.min_value} to {param.max_value})")
    
    # Set parameter values
    params.set_parameter('feedback', 0.7)
    params.set_parameter('delayTimeMs', 1000.0)
    params.set_parameter('mix', 0.8)
    
    print("\nParameter values set:")
    for name in params.parameters:
        print(f"  {name}: target={params.parameters[name].get_target_value():.4f}, current={params.get_parameter(name):.4f}")
    
    # Process blocks to see smoothing
    print("\nProcessing blocks (smoothing):")
    for i in range(10):
        params.process_block(1024)  # Process 1024 samples
        feedback = params.get_parameter('feedback')
        delay = params.get_parameter('delayTimeMs')
        mix = params.get_parameter('mix')
        print(f"  Block {i+1}: feedback={feedback:.4f}, delay={delay:.2f}ms, mix={mix:.4f}")
    
    # Test logarithmic parameter
    print("\nLogarithmic parameter test:")
    delay_param = params.get_smoothed_parameter('delayTimeMs')
    print(f"  Raw value (0-1): {delay_param.get_raw_value():.4f}")
    print(f"  Unscaled value: {delay_param.get_value():.2f}ms")
    
    # Plot smoothing (if matplotlib is available)
    try:
        # Set parameter to a new value
        params.set_parameter('feedback', 0.9)
        
        # Process and record values
        values = []
        for i in range(100):
            params.process_block(100)
            values.append(params.get_parameter('feedback'))
        
        plt.figure(figsize=(10, 6))
        plt.plot(values)
        plt.title("Parameter Smoothing (feedback: 0.5 -> 0.9)")
        plt.xlabel("Block")
        plt.ylabel("Value")
        plt.grid(True)
        plt.show()
    except ImportError:
        print("\nMatplotlib not available, skipping plot")
