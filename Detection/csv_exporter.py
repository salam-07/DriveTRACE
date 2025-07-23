"""
CSV export utilities for vehicle tracking data.
"""

import csv
from coordinate_transformer import CoordinateTransformer
from speed_calculator import SpeedCalculator

class CSVExporter:
    def __init__(self, output_path):
        self.output_path = output_path
        self.coordinate_transformer = None
    
    def set_coordinate_transformer(self, transformer):
        """Set the coordinate transformer for world coordinate conversion."""
        self.coordinate_transformer = transformer
    
    def export_vehicle_data(self, vehicle_data):
        """
        Export vehicle tracking data to CSV file.
        
        Args:
            vehicle_data: Dictionary containing tracking data for all vehicles
        """
        print(f"\nProcessing vehicle tracking data...")
        
        with open(self.output_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(['frame_id', 'vehicle_id', 'world_x', 'world_y', 'speed', 'action'])
            
            total_vehicles = len(vehicle_data)
            print(f"Processing data for {total_vehicles} vehicles...")
            
            for vehicle_id, data in vehicle_data.items():
                if data['initial_position'] is not None and len(data['positions']) > 0:
                    self._export_vehicle_trajectory(writer, vehicle_id, data)
        
        print(f"Data saved to: {self.output_path}")
    
    def _export_vehicle_trajectory(self, writer, vehicle_id, data):
        """Export trajectory data for a single vehicle."""
        for i in range(len(data['positions'])):
            pos = data['positions'][i]
            frame_id = data['frames'][i]
            
            # Convert coordinates to simulation world coordinates
            if self.coordinate_transformer:
                world_x, world_y = self.coordinate_transformer.to_simulation_coordinates(pos)
            else:
                # Fallback if no transformer is set
                world_x = int(pos[0] * 2)
                world_y = int(pos[1] * 5)
            
            # Get speed (already in simulation units)
            speed = data['speeds'][i] if i < len(data['speeds']) else 400
            
            # Determine action based on speed and movement patterns
            action = SpeedCalculator.determine_action(data, i, speed)
            
            writer.writerow([
                frame_id,
                vehicle_id,
                world_x,
                world_y,
                speed,
                action
            ])
    
    def validate_data(self, vehicle_data):
        """
        Validate vehicle data before export.
        
        Args:
            vehicle_data: Dictionary containing tracking data
            
        Returns:
            bool: True if data is valid for export
        """
        if not vehicle_data:
            print("Warning: No vehicle data to export")
            return False
        
        valid_vehicles = 0
        for vehicle_id, data in vehicle_data.items():
            if (data['initial_position'] is not None and 
                len(data['positions']) > 0 and 
                len(data['frames']) > 0):
                valid_vehicles += 1
        
        if valid_vehicles == 0:
            print("Warning: No valid vehicle trajectories found")
            return False
        
        print(f"Found {valid_vehicles} valid vehicle trajectories")
        return True
