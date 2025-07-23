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
    
    @staticmethod
    def determine_action(vehicle_data, current_index, speed):
        """
        Determine vehicle action based on speed and position changes.
        
        Args:
            vehicle_data: Dictionary containing vehicle tracking data
            current_index: Current index in the data arrays
            speed: Current speed value
            
        Returns:
            str: Action classification
        """
        # Speed-based actions (adjusted for 0-600 range)
        if speed > HIGH_SPEED_THRESHOLD:
            return 'speed_violation'
        elif speed > DANGEROUS_SPEED_THRESHOLD:
            return 'dangerous_swerve'
        elif speed < LOW_SPEED_THRESHOLD:
            return 'maintain'
        elif current_index > 0 and len(vehicle_data['speeds']) > current_index:
            prev_speed = vehicle_data['speeds'][current_index-1] if current_index-1 < len(vehicle_data['speeds']) else speed
            if speed > prev_speed * ACCELERATION_THRESHOLD:
                return 'accelerate'
        
        # Position-based actions (lane changes, swerving)
        if current_index > 0 and len(vehicle_data['positions']) > current_index:
            prev_pos = vehicle_data['positions'][current_index-1]
            curr_pos = vehicle_data['positions'][current_index]
            x_change = abs(curr_pos[0] - prev_pos[0])
            
            if x_change > LANE_CHANGE_THRESHOLD:
                return 'change_lane'
            elif x_change > SWERVE_THRESHOLD:
                return 'swerve'
        
        return 'maintain'
