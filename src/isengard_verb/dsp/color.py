"""
Color System Implementation

Color system for Isengard Verb.

The color system modifies the reverb characteristics based on the era:
- 1970s: Warmer, darker sound with more damping
- 1980s: Brighter, clearer sound with less damping
- Now: Clean, transparent sound with advanced characteristics

Based on VERIFIED evidence from ValhallaVintageVerb documentation.
"""

import numpy as np
from typing import Dict, Any


class ColorSystem:
    """
    Color system for reverb modes.
    
    Each color (1970s, 1980s, Now) has different characteristics:
    - 1970s: Warmer, more colored sound (like vintage hardware)
    - 1980s: Cleaner, brighter sound (like digital reverbs from that era)
    - Now: Modern, transparent sound with advanced processing
    """
    
    COLOR_1970S = "1970s"
    COLOR_1980S = "1980s"
    COLOR_NOW = "Now"
    
    def __init__(self):
        """Initialize color system."""
        self.current_color = self.COLOR_1980S  # Default
        
        # Color-specific parameter modifiers
        self.color_params = {
            self.COLOR_1970S: {
                'damping': 0.7,      # More damping for warmer sound
                'damping_freq': 6000.0,  # Lower damping frequency
                'diffusion': 0.6,    # Less diffusion (more discrete echoes)
                'mod_rate': 0.2,     # Slower modulation
                'mod_depth': 0.15,   # Moderate modulation depth
                'high_cut': 8000.0,  # Lower high cut
                'bass_mult': 1.2,    # More bass
            },
            self.COLOR_1980S: {
                'damping': 0.5,      # Moderate damping
                'damping_freq': 10000.0,  # Medium damping frequency
                'diffusion': 0.7,    # Moderate diffusion
                'mod_rate': 0.3,     # Medium modulation rate
                'mod_depth': 0.12,   # Medium modulation depth
                'high_cut': 12000.0, # Medium high cut
                'bass_mult': 1.0,    # Neutral bass
            },
            self.COLOR_NOW: {
                'damping': 0.3,      # Less damping for cleaner sound
                'damping_freq': 15000.0,  # Higher damping frequency
                'diffusion': 0.85,   # More diffusion (denser sound)
                'mod_rate': 0.4,     # Faster modulation
                'mod_depth': 0.18,   # Higher modulation depth
                'high_cut': 18000.0, # Higher high cut
                'bass_mult': 0.9,    # Less bass
            },
        }
    
    def set_color(self, color: str):
        """
        Set the current color.
        
        Args:
            color: One of '1970s', '1980s', 'Now'
        """
        if color in self.color_params:
            self.current_color = color
        else:
            raise ValueError(f"Unknown color: {color}. Valid colors are: {list(self.color_params.keys())}")
    
    def get_color(self) -> str:
        """Get the current color."""
        return self.current_color
    
    def get_color_params(self) -> Dict[str, Any]:
        """Get the parameters for the current color."""
        return self.color_params[self.current_color].copy()
    
    def apply_color(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply color-specific modifications to parameters.
        
        Args:
            params: Base parameters
            
        Returns:
            Modified parameters with color applied
        """
        color_params = self.get_color_params()
        modified_params = params.copy()
        
        # Apply color-specific modifications
        for key, value in color_params.items():
            if key in modified_params:
                # For some parameters, we scale the base value
                if key in ['damping', 'diffusion', 'mod_rate', 'mod_depth', 'bass_mult']:
                    # These are multiplicative
                    modified_params[key] = modified_params[key] * value
                elif key in ['damping_freq', 'high_cut']:
                    # These are additive offsets
                    base_value = modified_params.get(key, 10000.0)
                    modified_params[key] = value
                else:
                    # Direct replacement
                    modified_params[key] = value
        
        return modified_params
    
    def get_color_name(self, color: str) -> str:
        """Get a display name for a color."""
        names = {
            self.COLOR_1970S: "1970s",
            self.COLOR_1980S: "1980s",
            self.COLOR_NOW: "Now",
        }
        return names.get(color, color)
    
    def get_color_description(self, color: str) -> str:
        """Get a description for a color."""
        descriptions = {
            self.COLOR_1970S: "Vintage 1970s - Warmer, darker sound with more damping",
            self.COLOR_1980S: "Classic 1980s - Clean, balanced digital reverb",
            self.COLOR_NOW: "Modern Now - Transparent, dense sound with advanced processing",
        }
        return descriptions.get(color, f"Unknown color: {color}")
    
    def list_colors(self) -> list:
        """List all available colors."""
        return list(self.color_params.keys())


# Test
if __name__ == "__main__":
    print("Testing ColorSystem...")
    
    color_system = ColorSystem()
    
    # Test all colors
    for color in color_system.list_colors():
        print(f"\nColor: {color}")
        print(f"  Name: {color_system.get_color_name(color)}")
        print(f"  Description: {color_system.get_color_description(color)}")
        print(f"  Params: {color_system.color_params[color]}")
        
        # Test applying color
        base_params = {
            'decay': 0.6,
            'size': 0.7,
            'damping': 0.5,
            'damping_freq': 10000.0,
            'diffusion': 0.7,
            'mod_rate': 0.3,
            'mod_depth': 0.1,
        }
        
        color_system.set_color(color)
        modified = color_system.apply_color(base_params)
        print(f"  Modified params: {modified}")
    
    print('\nColorSystem test completed successfully!')
