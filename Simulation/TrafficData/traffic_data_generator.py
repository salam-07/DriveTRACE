import pandas as pd
import numpy as np
from pathlib import Path
import random

class TrafficDataGenerator:
    def __init__(self):
        self.frame_rate = 30  # frames per second
        self.duration = 30   # seconds
        self.total_frames = self.frame_rate * self.duration
        self.world_width = 1200  # Total world width
        self.world_length = 3000  # Total world length
        self.num_vehicles = 10
        self.min_speed = 50  # pixels per second
        self.max_speed = 120  # pixels per second
        self.lane_width = 100  # Width of a lane
        self.num_lanes = 4
        self.lane_change_probability = 0.02  # Probability of initiating a lane change
        self.speed_change_probability = 0.05  # Probability of changing speed
        
    def generate_vehicle_path(self, vehicle_id):
        """Generate a realistic path for a single vehicle"""
        data = []
        
        # Initial position and speed
        x_pos = random.uniform(50, self.road_width - 50)  # Start somewhere on the road width
        y_pos = random.uniform(0, self.road_length)       # Start somewhere along the road length
        speed = random.uniform(self.min_speed, self.max_speed)
        
        # Generate slight variations in movement
        for frame in range(self.total_frames):
            # Add some natural variation to speed
            if random.random() < 0.1:  # 10% chance to change speed
                speed += random.uniform(-5, 5)
                speed = np.clip(speed, self.min_speed, self.max_speed)
            
            # Add slight lateral movement (lane changes)
            if random.random() < 0.02:  # 2% chance to start lane change
                target_x = random.uniform(50, self.road_width - 50)
                x_pos += np.sign(target_x - x_pos) * 2
            
            # Keep vehicle within road bounds
            x_pos = np.clip(x_pos, 0, self.road_width)
            y_pos = (y_pos + speed / self.frame_rate) % self.road_length
            
            data.append({
                'frame': frame,
                'vehicle_id': vehicle_id,
                'x_position': x_pos,
                'y_position': y_pos,
                'speed_px_per_s': speed,
                'relative_x': 0,  # Will be calculated later
                'relative_y': 0   # Will be calculated later
            })
            
        return data
    
    def generate_traffic_data(self, output_path):
        """Generate traffic data for multiple vehicles"""
        all_data = []
        
        # Generate path for each vehicle
        for vehicle_id in range(self.num_vehicles):
            vehicle_data = self.generate_vehicle_path(vehicle_id)
            all_data.extend(vehicle_data)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        
        # Calculate relative positions from initial positions
        for vehicle_id in range(self.num_vehicles):
            vehicle_df = df[df['vehicle_id'] == vehicle_id]
            initial_x = vehicle_df.iloc[0]['x_position']
            initial_y = vehicle_df.iloc[0]['y_position']
            
            mask = df['vehicle_id'] == vehicle_id
            df.loc[mask, 'relative_x'] = df.loc[mask, 'x_position'] - initial_x
            df.loc[mask, 'relative_y'] = df.loc[mask, 'y_position'] - initial_y
        
        # Sort by frame and vehicle_id
        df = df.sort_values(['frame', 'vehicle_id'])
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        print(f"Generated traffic data saved to: {output_path}")
        return df

def main():
    generator = TrafficDataGenerator()
    output_file = "traffic_data_4.csv"
    generator.generate_traffic_data(output_file)

if __name__ == "__main__":
    main()
