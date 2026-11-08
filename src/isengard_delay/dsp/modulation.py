# Modulation Sources
# LFO and modulation for Isengard Delay

"""
Modulation sources for Isengard Delay.

Features:
- LFO with multiple waveforms (Sine, Triangle, Saw, Square, Random)
- Mode-specific modulation characteristics
- Hardwired modulation for diffusion network

Based on VERIFIED evidence from official Valhalla documentation.

Usage:
    from isengard_delay.dsp.modulation import LFO, ModulationSystem
    
    # Create LFO
    lfo = LFO(rate_hz=1.0, depth=0.5, waveform='sine', sample_rate=44100)
    
    # Get current value
    value = lfo.get_value()
    
    # Process block
    lfo.process_block(num_samples)
"""

import numpy as np


class LFO:
    """
    Low-Frequency Oscillator for modulation.
    
    Generates periodic waveforms for modulating various parameters.
    
    Parameters:
        rate_hz (float): Oscillation rate in Hz
        depth (float): Modulation depth (0.0 to 1.0)
        waveform (str): Waveform type ('sine', 'triangle', 'saw', 'square', 'random')
        sample_rate (float): Sample rate in Hz (default: 44100)
        phase (float): Initial phase in radians (default: 0.0)
    """
    
    def __init__(self, rate_hz, depth, waveform='sine', sample_rate=44100, phase=0.0):
        """
        Initialize the LFO.
        
        Args:
            rate_hz: Oscillation rate in Hz
            depth: Modulation depth (0.0 to 1.0)
            waveform: Waveform type
            sample_rate: Sample rate in Hz
            phase: Initial phase in radians
        """
        self.rate_hz = float(rate_hz)
        self.depth = float(np.clip(depth, 0.0, 1.0))
        self.waveform = waveform.lower()
        self.sample_rate = float(sample_rate)
        self.phase = float(phase)
        
        # Random state for random waveform
        self.random_state = np.random.RandomState()
        self.random_value = 0.0
    
    def set_rate(self, rate_hz):
        """
        Set the oscillation rate.
        
        Args:
            rate_hz: New rate in Hz
        """
        self.rate_hz = float(rate_hz)
    
    def set_depth(self, depth):
        """
        Set the modulation depth.
        
        Args:
            depth: New depth (0.0 to 1.0)
        """
        self.depth = float(np.clip(depth, 0.0, 1.0))
    
    def set_waveform(self, waveform):
        """
        Set the waveform type.
        
        Args:
            waveform: Waveform type ('sine', 'triangle', 'saw', 'square', 'random')
        """
        self.waveform = waveform.lower()
    
    def set_sample_rate(self, sample_rate):
        """
        Set the sample rate.
        
        Args:
            sample_rate: New sample rate in Hz
        """
        self.sample_rate = float(sample_rate)
    
    def set_phase(self, phase):
        """
        Set the initial phase.
        
        Args:
            phase: New phase in radians
        """
        self.phase = float(phase)
    
    def get_value(self):
        """
        Get the current LFO value.
        
        Returns:
            float: Current value (-depth to +depth)
        """
        # Calculate base value based on waveform
        if self.waveform == 'sine':
            base = np.sin(self.phase)
        elif self.waveform == 'triangle':
            base = self._triangle(self.phase)
        elif self.waveform == 'saw':
            base = self._saw(self.phase)
        elif self.waveform == 'square':
            base = self._square(self.phase)
        elif self.waveform == 'random':
            base = self.random_value
        else:
            base = np.sin(self.phase)  # Default to sine
        
        return base * self.depth
    
    def process_sample(self):
        """
        Process one sample and update the LFO state.
        
        Returns:
            float: Current LFO value
        """
        # Update phase
        phase_increment = 2.0 * np.pi * self.rate_hz / self.sample_rate
        self.phase += phase_increment
        
        # Wrap phase
        if self.phase >= 2.0 * np.pi:
            self.phase -= 2.0 * np.pi
        elif self.phase < 0:
            self.phase += 2.0 * np.pi
        
        # For random waveform, generate new random value at each cycle
        if self.waveform == 'random':
            if self.phase < phase_increment:  # Start of new cycle
                self.random_value = self.random_state.uniform(-1.0, 1.0)
        
        return self.get_value()
    
    def process_block(self, num_samples):
        """
        Process a block of samples and update the LFO state.
        
        Args:
            num_samples: Number of samples to process
        """
        for _ in range(num_samples):
            self.process_sample()
    
    def _triangle(self, phase):
        """
        Triangle waveform.
        
        Args:
            phase: Phase in radians
            
        Returns:
            float: Triangle value (-1 to 1)
        """
        # Normalize phase to [0, 2pi]
        phase = phase % (2.0 * np.pi)
        
        # Triangle: 2 * (phase / (2pi) - 0.5) for phase in [0, pi]
        #          -2 * (phase / (2pi) - 1.5) for phase in [pi, 2pi]
        if phase < np.pi:
            return 2.0 * (phase / (2.0 * np.pi) - 0.5)
        else:
            return -2.0 * (phase / (2.0 * np.pi) - 1.5)
    
    def _saw(self, phase):
        """
        Sawtooth waveform.
        
        Args:
            phase: Phase in radians
            
        Returns:
            float: Sawtooth value (-1 to 1)
        """
        # Normalize phase to [0, 2pi]
        phase = phase % (2.0 * np.pi)
        
        # Saw: 2 * (phase / (2pi) - 0.5)
        return 2.0 * (phase / (2.0 * np.pi) - 0.5)
    
    def _square(self, phase):
        """
        Square waveform.
        
        Args:
            phase: Phase in radians
            
        Returns:
            float: Square value (-1 to 1)
        """
        # Normalize phase to [0, 2pi]
        phase = phase % (2.0 * np.pi)
        
        # Square: 1 for phase in [0, pi), -1 for phase in [pi, 2pi)
        if phase < np.pi:
            return 1.0
        else:
            return -1.0
    
    def reset(self):
        """Reset the LFO to initial state."""
        self.phase = 0.0
        self.random_state = np.random.RandomState()
        self.random_value = 0.0


class WowFlutterLFO:
    """
    Wow and Flutter LFO for Tape mode.
    
    Specialized LFO for emulating tape wow and flutter.
    - Wow: Slow random modulation (0.1-2 Hz)
    - Flutter: Fast random modulation (2-20 Hz)
    
    Based on VERIFIED evidence E012 from official Valhalla documentation.
    
    Parameters:
        sample_rate (float): Sample rate in Hz (default: 44100)
        delay_time_ms (float): Current delay time in milliseconds
    """
    
    def __init__(self, sample_rate=44100, delay_time_ms=500.0):
        """
        Initialize the Wow and Flutter LFO.
        
        Args:
            sample_rate: Sample rate in Hz
            delay_time_ms: Initial delay time in milliseconds
        """
        self.sample_rate = float(sample_rate)
        self.delay_time_ms = float(delay_time_ms)
        
        # Wow LFO: slow random modulation
        self.wow_lfo = LFO(
            rate_hz=1.0,  # Will be updated based on delay time
            depth=0.1,
            waveform='random',
            sample_rate=sample_rate
        )
        
        # Flutter LFO: fast random modulation
        self.flutter_lfo = LFO(
            rate_hz=10.0,  # Will be updated based on delay time
            depth=0.05,
            waveform='random',
            sample_rate=sample_rate
        )
        
        # Update rates based on delay time
        self._update_rates()
    
    def set_delay_time(self, delay_time_ms):
        """
        Set the delay time and update wow/flutter rates.
        
        Based on VERIFIED evidence E012: Wow/Flutter rates are functions of delay time.
        - Wow rate: 1000ms / delayTimeMs (clamped to 0.1-2Hz)
        - Flutter rate: Wow rate * 10
        
        Args:
            delay_time_ms: New delay time in milliseconds
        """
        self.delay_time_ms = float(delay_time_ms)
        self._update_rates()
    
    def _update_rates(self):
        """Update wow and flutter rates based on delay time."""
        # Wow rate: 1000ms / delayTimeMs (clamped to 0.1-2Hz)
        wow_rate = 1000.0 / self.delay_time_ms
        wow_rate = np.clip(wow_rate, 0.1, 2.0)
        self.wow_lfo.set_rate(wow_rate)
        
        # Flutter rate: Wow rate * 10 (2-20Hz)
        flutter_rate = wow_rate * 10.0
        flutter_rate = np.clip(flutter_rate, 2.0, 20.0)
        self.flutter_lfo.set_rate(flutter_rate)
    
    def set_wow_depth(self, depth):
        """
        Set the wow depth.
        
        Args:
            depth: Wow depth (0.0 to 1.0)
        """
        self.wow_lfo.set_depth(depth)
    
    def set_flutter_depth(self, depth):
        """
        Set the flutter depth.
        
        Args:
            depth: Flutter depth (0.0 to 1.0)
        """
        self.flutter_lfo.set_depth(depth)
    
    def get_value(self):
        """
        Get the combined wow + flutter modulation value.
        
        Returns:
            float: Combined modulation value
        """
        wow_value = self.wow_lfo.get_value()
        flutter_value = self.flutter_lfo.get_value()
        return wow_value + flutter_value
    
    def get_values(self):
        """
        Get separate wow and flutter modulation values.
        
        Returns:
            tuple: (wow_value, flutter_value)
        """
        wow_value = self.wow_lfo.get_value()
        flutter_value = self.flutter_lfo.get_value()
        return wow_value, flutter_value
    
    def process_sample(self):
        """
        Process one sample and update both LFOs.
        
        Returns:
            float: Combined modulation value
        """
        self.wow_lfo.process_sample()
        self.flutter_lfo.process_sample()
        return self.get_value()
    
    def process_block(self, num_samples):
        """
        Process a block of samples.
        
        Args:
            num_samples: Number of samples to process
        """
        self.wow_lfo.process_block(num_samples)
        self.flutter_lfo.process_block(num_samples)
    
    def reset(self):
        """Reset both LFOs to initial state."""
        self.wow_lfo.reset()
        self.flutter_lfo.reset()


class ModulationSystem:
    """
    Complete modulation system for Isengard Delay.
    
    Manages all modulation sources for the delay plugin.
    
    Parameters:
        sample_rate (float): Sample rate in Hz (default: 44100)
    """
    
    def __init__(self, sample_rate=44100):
        """
        Initialize the modulation system.
        
        Args:
            sample_rate: Sample rate in Hz
        """
        self.sample_rate = float(sample_rate)
        
        # Global modulation LFO
        self.global_lfo = LFO(
            rate_hz=1.0,
            depth=0.0,
            waveform='sine',
            sample_rate=sample_rate
        )
        
        # Wow/Flutter LFO for Tape mode
        self.wow_flutter_lfo = WowFlutterLFO(sample_rate=sample_rate)
        
        # Clock jitter LFO for BBD mode
        self.clock_jitter_lfo = LFO(
            rate_hz=10.0,
            depth=0.0,
            waveform='random',
            sample_rate=sample_rate
        )
        
        # Current mode (affects which modulation is active)
        self.current_mode = None
    
    def set_sample_rate(self, sample_rate):
        """
        Set the sample rate for all LFOs.
        
        Args:
            sample_rate: New sample rate in Hz
        """
        self.sample_rate = float(sample_rate)
        self.global_lfo.set_sample_rate(sample_rate)
        self.wow_flutter_lfo.set_sample_rate(sample_rate)
        self.clock_jitter_lfo.set_sample_rate(sample_rate)
    
    def set_mode(self, mode):
        """
        Set the current mode.
        
        Args:
            mode: Current mode ('Tape', 'HiFi', 'BBD', 'Digital', 'Ghost', 'Pitch', 'RevPitch')
        """
        self.current_mode = mode
        
        # Update wow/flutter delay time if in Tape mode
        if mode == 'Tape':
            # Will be updated when delay time is set
            pass
    
    def set_delay_time(self, delay_time_ms):
        """
        Set the delay time (for Tape mode wow/flutter).
        
        Args:
            delay_time_ms: Delay time in milliseconds
        """
        self.wow_flutter_lfo.set_delay_time(delay_time_ms)
    
    def set_global_modulation(self, rate_hz, depth, waveform):
        """
        Set global modulation parameters.
        
        Args:
            rate_hz: Modulation rate in Hz
            depth: Modulation depth (0.0 to 1.0)
            waveform: Waveform type
        """
        self.global_lfo.set_rate(rate_hz)
        self.global_lfo.set_depth(depth)
        self.global_lfo.set_waveform(waveform)
    
    def set_wow_flutter(self, wow_depth, flutter_depth):
        """
        Set wow and flutter depths (for Tape mode).
        
        Args:
            wow_depth: Wow depth (0.0 to 1.0)
            flutter_depth: Flutter depth (0.0 to 1.0)
        """
        self.wow_flutter_lfo.set_wow_depth(wow_depth)
        self.wow_flutter_lfo.set_flutter_depth(flutter_depth)
    
    def set_clock_jitter(self, rate_hz, depth):
        """
        Set clock jitter parameters (for BBD mode).
        
        Args:
            rate_hz: Jitter rate in Hz
            depth: Jitter depth (0.0 to 1.0)
        """
        self.clock_jitter_lfo.set_rate(rate_hz)
        self.clock_jitter_lfo.set_depth(depth)
    
    def get_modulation_value(self):
        """
        Get the current modulation value based on mode.
        
        Returns:
            float: Modulation value
        """
        if self.current_mode == 'Tape':
            return self.wow_flutter_lfo.get_value()
        elif self.current_mode == 'BBD':
            return self.clock_jitter_lfo.get_value()
        else:
            return self.global_lfo.get_value()
    
    def process_sample(self):
        """
        Process one sample and update all active LFOs.
        
        Returns:
            float: Current modulation value
        """
        if self.current_mode == 'Tape':
            value = self.wow_flutter_lfo.process_sample()
        elif self.current_mode == 'BBD':
            value = self.clock_jitter_lfo.process_sample()
        else:
            value = self.global_lfo.process_sample()
        
        return value
    
    def process_block(self, num_samples):
        """
        Process a block of samples.
        
        Args:
            num_samples: Number of samples to process
        """
        if self.current_mode == 'Tape':
            self.wow_flutter_lfo.process_block(num_samples)
        elif self.current_mode == 'BBD':
            self.clock_jitter_lfo.process_block(num_samples)
        else:
            self.global_lfo.process_block(num_samples)
    
    def reset(self):
        """Reset all LFOs to initial state."""
        self.global_lfo.reset()
        self.wow_flutter_lfo.reset()
        self.clock_jitter_lfo.reset()


# Example usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    print("Modulation System Example")
    print("=" * 50)
    
    # Create modulation system
    mod_system = ModulationSystem(sample_rate=44100)
    
    # Test global LFO
    print("\nTesting Global LFO (Sine, 1Hz, depth=0.5):")
    mod_system.set_global_modulation(rate_hz=1.0, depth=0.5, waveform='sine')
    mod_system.set_mode('HiFi')
    
    values = []
    for i in range(1000):
        values.append(mod_system.process_sample())
    
    print(f"  Min: {min(values):.4f}, Max: {max(values):.4f}")
    
    # Test Wow/Flutter LFO
    print("\nTesting Wow/Flutter LFO (Tape mode, delay=500ms):")
    mod_system.set_mode('Tape')
    mod_system.set_delay_time(500.0)
    mod_system.set_wow_flutter(wow_depth=0.3, flutter_depth=0.2)
    
    values = []
    for i in range(1000):
        values.append(mod_system.process_sample())
    
    print(f"  Min: {min(values):.4f}, Max: {max(values):.4f}")
    
    # Test Clock Jitter LFO
    print("\nTesting Clock Jitter LFO (BBD mode):")
    mod_system.set_mode('BBD')
    mod_system.set_clock_jitter(rate_hz=10.0, depth=0.1)
    
    values = []
    for i in range(1000):
        values.append(mod_system.process_sample())
    
    print(f"  Min: {min(values):.4f}, Max: {max(values):.4f}")
    
    # Test different waveforms
    print("\nTesting different waveforms:")
    mod_system.set_mode('HiFi')
    for waveform in ['sine', 'triangle', 'saw', 'square']:
        mod_system.set_global_modulation(rate_hz=1.0, depth=0.5, waveform=waveform)
        mod_system.reset()
        
        values = []
        for i in range(100):
            values.append(mod_system.process_sample())
        
        print(f"  {waveform.capitalize()}: Min={min(values):.4f}, Max={max(values):.4f}")
    
    # Plot (if matplotlib is available)
    try:
        # Generate LFO values for plotting
        mod_system.set_global_modulation(rate_hz=1.0, depth=0.5, waveform='sine')
        mod_system.reset()
        
        values_sine = []
        for i in range(1000):
            values_sine.append(mod_system.process_sample())
        
        mod_system.set_global_modulation(rate_hz=1.0, depth=0.5, waveform='triangle')
        mod_system.reset()
        
        values_triangle = []
        for i in range(1000):
            values_triangle.append(mod_system.process_sample())
        
        mod_system.set_global_modulation(rate_hz=1.0, depth=0.5, waveform='saw')
        mod_system.reset()
        
        values_saw = []
        for i in range(1000):
            values_saw.append(mod_system.process_sample())
        
        mod_system.set_global_modulation(rate_hz=1.0, depth=0.5, waveform='square')
        mod_system.reset()
        
        values_square = []
        for i in range(1000):
            values_square.append(mod_system.process_sample())
        
        plt.figure(figsize=(12, 8))
        
        plt.subplot(4, 1, 1)
        plt.plot(values_sine)
        plt.title("Sine Waveform")
        plt.xlabel("Sample")
        plt.ylabel("Value")
        plt.grid(True)
        plt.ylim(-0.6, 0.6)
        
        plt.subplot(4, 1, 2)
        plt.plot(values_triangle)
        plt.title("Triangle Waveform")
        plt.xlabel("Sample")
        plt.ylabel("Value")
        plt.grid(True)
        plt.ylim(-0.6, 0.6)
        
        plt.subplot(4, 1, 3)
        plt.plot(values_saw)
        plt.title("Sawtooth Waveform")
        plt.xlabel("Sample")
        plt.ylabel("Value")
        plt.grid(True)
        plt.ylim(-0.6, 0.6)
        
        plt.subplot(4, 1, 4)
        plt.plot(values_square)
        plt.title("Square Waveform")
        plt.xlabel("Sample")
        plt.ylabel("Value")
        plt.grid(True)
        plt.ylim(-0.6, 0.6)
        
        plt.tight_layout()
        plt.show()
    except ImportError:
        print("\nMatplotlib not available, skipping plots")
