"""
Synthetic Traffic Data Generator
Generates realistic CSV traffic data files for the DriveTRACE simulation.
"""

import pandas as pd
import numpy as np
import random
import os
import math

class TrafficDataGenerator:
    def __init__(self, window_width=800, lane_width=150, num_lanes=4):
        self.window_width = window_width
        self.lane_width = lane_width
        self.num_lanes = num_lanes
        self.lane_centers = [(i * lane_width) + (lane_width // 2) for i in range(num_lanes)]
        
    def generate_vehicle_trajectory(self, vehicle_id, start_frame, duration, lane, 
                                  base_speed=200, speed_variation=50):
        """Generate a realistic vehicle trajectory"""
        trajectory = []
        
        # Random starting position and speed
        start_y = random.uniform(0, 2000)
        current_speed = base_speed + random.uniform(-speed_variation, speed_variation)
        current_y = start_y
        current_x = self.lane_centers[lane]
        
        # Add some randomness to lane positioning
        lane_offset = random.uniform(-self.lane_width * 0.2, self.lane_width * 0.2)
        current_x += lane_offset
        
        for frame in range(start_frame, start_frame + duration):
            # Add realistic speed variations
            speed_change = random.uniform(-10, 10)
            current_speed = max(50, min(400, current_speed + speed_change))
            
            # Update position
            current_y += current_speed * (1/60)  # Assuming 60 FPS
            
            # Occasional lane changes
            if random.random() < 0.001 and duration > 100:  # 0.1% chance per frame
                # Change lane gradually
                target_lane = max(0, min(self.num_lanes - 1, lane + random.choice([-1, 1])))
                target_x = self.lane_centers[target_lane] + random.uniform(-self.lane_width * 0.2, self.lane_width * 0.2)
                current_x += (target_x - current_x) * 0.02  # Gradual lane change
            
            # Add slight horizontal drift
            current_x += random.uniform(-1, 1)
            
            # Keep within lane bounds
            min_x = lane * self.lane_width + 10
            max_x = (lane + 1) * self.lane_width - 10
            current_x = max(min_x, min(max_x, current_x))
            
            trajectory.append({
                'frame_id': frame,
                'vehicle_id': vehicle_id,
                'world_x': int(current_x),
                'world_y': int(current_y),
                'speed': int(current_speed)
            })
            
        return trajectory
    
    def generate_traffic_scenarios(self, total_frames=2000, num_vehicles=5):
        """Generate different traffic scenarios"""
        all_trajectories = []
        
        # Scenario 1: Normal flowing traffic
        for i in range(num_vehicles):
            vehicle_id = i + 1
            
            # Stagger vehicle appearances
            start_frame = random.randint(0, 300)
            duration = random.randint(800, total_frames - start_frame)
            
            # Distribute vehicles across lanes
            lane = i % self.num_lanes
            
            # Vary speeds based on lane (rightmost lanes typically faster)
            base_speed = 150 + (lane * 50) + random.randint(-30, 30)
            
            trajectory = self.generate_vehicle_trajectory(
                vehicle_id, start_frame, duration, lane, base_speed
            )
            all_trajectories.extend(trajectory)
        
        # Scenario 2: Add some congestion periods
        if random.random() < 0.3:  # 30% chance of congestion
            congestion_start = random.randint(500, 1000)
            congestion_duration = random.randint(200, 400)
            
            # Slow down existing vehicles during congestion
            for trajectory in all_trajectories:
                if (congestion_start <= trajectory['frame_id'] <= 
                    congestion_start + congestion_duration):
                    trajectory['speed'] = max(30, int(trajectory['speed'] * 0.4))
        
        return all_trajectories
    
    def add_realistic_spacing(self, trajectories):
        """Ensure realistic spacing between vehicles"""
        # Group by frame
        frame_groups = {}
        for traj in trajectories:
            frame_id = traj['frame_id']
            if frame_id not in frame_groups:
                frame_groups[frame_id] = []
            frame_groups[frame_id].append(traj)
        
        # Check and adjust spacing for each frame
        for frame_id, vehicles in frame_groups.items():
            if len(vehicles) <= 1:
                continue
                
            # Sort by lane and position
            vehicles.sort(key=lambda v: (v['world_x'], v['world_y']))
            
            for i in range(len(vehicles) - 1):
                v1 = vehicles[i]
                v2 = vehicles[i + 1]
                
                # Check if vehicles are in similar lanes and too close
                x_diff = abs(v1['world_x'] - v2['world_x'])
                y_diff = abs(v1['world_y'] - v2['world_y'])
                
                if x_diff < self.lane_width * 0.8 and y_diff < 100:
                    # Separate vehicles
                    if v1['world_y'] < v2['world_y']:
                        v2['world_y'] = v1['world_y'] + 120
                    else:
                        v1['world_y'] = v2['world_y'] + 120
        
        return trajectories
    
    def generate_csv_file(self, filename, total_frames=2000, num_vehicles=5, 
                         add_spacing=True):
        """Generate a complete CSV traffic data file"""
        print(f"Generating traffic data: {num_vehicles} vehicles, {total_frames} frames")
        
        # Generate basic trajectories
        trajectories = self.generate_traffic_scenarios(total_frames, num_vehicles)
        
        # Add realistic spacing if requested
        if add_spacing:
            trajectories = self.add_realistic_spacing(trajectories)
        
        # Convert to DataFrame and sort
        df = pd.DataFrame(trajectories)
        df = df.sort_values(['frame_id', 'vehicle_id'])
        
        # Save to CSV
        filepath = os.path.join(os.path.dirname(__file__), filename)
        df.to_csv(filepath, index=False)
        
        print(f"Generated {len(df)} traffic data points")
        print(f"Vehicles: {sorted(df['vehicle_id'].unique())}")
        print(f"Frame range: {df['frame_id'].min()} - {df['frame_id'].max()}")
        print(f"Saved to: {filepath}")
        
        return df

def main():
    """Generate multiple traffic data files with different scenarios"""
    generator = TrafficDataGenerator()
    
    # Generate various scenarios
    scenarios = [
        {"filename": "traffic_data_light.csv", "num_vehicles": 3, "frames": 1500},
        {"filename": "traffic_data_medium.csv", "num_vehicles": 5, "frames": 2000},
        {"filename": "traffic_data_heavy.csv", "num_vehicles": 8, "frames": 2500},
        {"filename": "traffic_data_rush_hour.csv", "num_vehicles": 12, "frames": 3000},
    ]
    
    for scenario in scenarios:
        print(f"\n{'='*50}")
        print(f"Generating: {scenario['filename']}")
        print(f"{'='*50}")
        
        df = generator.generate_csv_file(
            filename=scenario["filename"],
            total_frames=scenario["frames"],
            num_vehicles=scenario["num_vehicles"]
        )
        
        # Print some statistics
        print(f"\nStatistics for {scenario['filename']}:")
        print(f"  Average speed: {df['speed'].mean():.1f}")
        print(f"  Speed range: {df['speed'].min()} - {df['speed'].max()}")
        print(f"  Vehicles per frame (avg): {len(df) / scenario['frames']:.1f}")

if __name__ == "__main__":
    main()
