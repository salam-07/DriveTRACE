"""
Speed calculation utilities for vehicle tracking.
"""

import numpy as np
from detection_config import *

class SpeedCalculator:
    def __init__(self, fps):
        self.fps = fps
    
    def calculate_speeds(self, positions, frames):
        """
        Calculate display and simulation speeds from position data.
        
        Args:
            positions: List of (x, y) positions
            frames: List of frame numbers
            
        Returns:
            tuple: (display_speed_px_per_sec, simulation_speed)
        """
        if len(positions) < 2 or len(frames) < 2:
            return 0, DEFAULT_SIMULATION_SPEED
        
        # Get last two positions and frames
        pos1 = positions[-2]
        pos2 = positions[-1]
        frame1 = frames[-2]
        frame2 = frames[-1]
        
        time_diff = (frame2 - frame1) / self.fps
        if time_diff <= 0:
            return 0, DEFAULT_SIMULATION_SPEED
        
        # Calculate speed in pixels per second for display
        distance = np.linalg.norm(np.array(pos2) - np.array(pos1))
        speed_display = int(distance / time_diff)
        
        # Map pixel speed to simulation speed range (0-600)
        if speed_display == 0:
            speed_simulation = 0  # Stopped
        else:
            # Scale pixel speed to simulation range, with some base speed
            speed_simulation = min(
                SIMULATION_SPEED_RANGE[1], 
                max(100, int(speed_display * SPEED_SCALE_FACTOR + BASE_SIMULATION_SPEED))
            )
        
        return speed_display, speed_simulation
