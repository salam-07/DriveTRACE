import pygame
import pandas as pd
import os
import random
from config import *

class CSVTrafficVehicle:
    def __init__(self, vehicle_id, lane, world_y, speed, action="maintain"):
        # Load random vehicle image
        vehicle_files = [f for f in os.listdir(TRAFFIC_ASSET_DIR) 
                        if f.startswith('car_')]
        vehicle_image = random.choice(vehicle_files)
        self.original_image = pygame.image.load(f'{TRAFFIC_ASSET_DIR}/{vehicle_image}').convert_alpha()
        
        # Scale the vehicle
        new_width = int(LANE_WIDTH * VEHICLE_SCALE)
        new_height = int((new_width / self.original_image.get_width()) * self.original_image.get_height())
        self.original_image = pygame.transform.smoothscale(self.original_image, (new_width, new_height))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        
        # Vehicle properties
        self.vehicle_id = vehicle_id
        self.lane = lane
        self.world_y = world_y
        self.speed = speed
        self.action = action
        self.target_lane = lane
        self.lane_change_progress = 0
        self.lane_change_speed = 0.05  # How fast lane changes occur
        
        # For smooth interpolation between CSV data points
        self.target_speed = speed
        
    def update(self, player_speed, player_lane, dt):
        """Update vehicle position and state"""
        # Smooth interpolation to target speed
        self.speed += (self.target_speed - self.speed) * 0.02
        
        # Handle lane changes
        if self.target_lane != self.lane:
            self.lane_change_progress += self.lane_change_speed
            if self.lane_change_progress >= 1.0:
                self.lane = self.target_lane
                self.lane_change_progress = 0
        
        # Calculate current lane position (for smooth lane changes)
        if self.lane_change_progress > 0:
            current_lane_float = self.lane + (self.target_lane - self.lane) * self.lane_change_progress
        else:
            current_lane_float = float(self.lane)
        
        self.current_lane_float = current_lane_float
        
        # Move relative to player with natural vehicle movement
        speed_difference = player_speed - self.speed
        self.world_y -= speed_difference * dt
    
    def get_screen_pos(self, player_world_y, center_y):
        return int(center_y - (self.world_y - player_world_y))
    
    def draw(self, screen, player_world_y, center_y):
        # Use current_lane_float for smooth lane changes
        base_x = int((self.current_lane_float + 0.5) * LANE_WIDTH)
        base_y = self.get_screen_pos(player_world_y, center_y)
        
        self.rect.centerx = base_x
        self.rect.centery = base_y
        screen.blit(self.image, self.rect)

class CSVTrafficManager:
    def __init__(self, csv_file_path="TrafficData/traffic_data_2.csv"):
        self.csv_file_path = os.path.join(os.path.dirname(__file__), csv_file_path)
        self.vehicles = {}
        self.enabled = False
        self.current_frame = 0
        self.max_frame = 0
        self.df = None
        self.load_csv_data()
        
    def load_csv_data(self):
        """Load traffic data from CSV file"""
        try:
            self.df = pd.read_csv(self.csv_file_path)
            self.max_frame = self.df['frame_id'].max()
            print(f"Loaded traffic data: {len(self.df)} entries, max frame: {self.max_frame}")
            
            # Get unique vehicle IDs
            self.vehicle_ids = self.df['vehicle_id'].unique()
            print(f"Vehicle IDs: {self.vehicle_ids}")
            
        except FileNotFoundError:
            print(f"CSV file not found: {self.csv_file_path}")
            self.df = pd.DataFrame()
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            self.df = pd.DataFrame()
    
    def toggle(self):
        """Toggle traffic on/off"""
        self.enabled = not self.enabled
        if self.enabled and self.df is not None and not self.df.empty:
            self.initialize_vehicles()
    
    def initialize_vehicles(self):
        """Initialize vehicles from CSV data"""
        self.vehicles = {}
        # Get initial frame data (frame 0)
        initial_frame = self.df[self.df['frame_id'] == 0]
        
        for _, row in initial_frame.iterrows():
            vehicle_id = row['vehicle_id']
            # Create vehicles with spread out positions around the player
            random_offset = random.uniform(-800, 1500)  # Spread vehicles around player
            
            self.vehicles[vehicle_id] = CSVTrafficVehicle(
                vehicle_id=vehicle_id,
                lane=row['lane'],
                world_y=random_offset,  # Position relative to start
                speed=row['speed'],
                action=row['action']
            )
    
    def update(self, player_speed, player_lane, player_world_y):
        """Update all traffic vehicles"""
        if not self.enabled or self.df is None or self.df.empty:
            return
        
        # Update frame counter very slowly
        self.current_frame += 0.1  # Even slower frame advancement
        
        # Loop the CSV data
        if self.current_frame > self.max_frame:
            self.current_frame = 0
        
        # Get current frame data
        current_frame_int = int(self.current_frame)
        frame_data = self.df[self.df['frame_id'] == current_frame_int]
        
        # Update each vehicle with CSV data, but only speed and lane changes
        for _, row in frame_data.iterrows():
            vehicle_id = row['vehicle_id']
            if vehicle_id in self.vehicles:
                # Only update speed and lane, not position
                self.vehicles[vehicle_id].target_speed = row['speed']
                self.vehicles[vehicle_id].action = row['action']
                
                # Handle lane changes
                if row['lane'] != self.vehicles[vehicle_id].lane:
                    self.vehicles[vehicle_id].target_lane = row['lane']
                    self.vehicles[vehicle_id].lane_change_progress = 0
        
        # Update vehicle physics
        dt = 1/FPS
        for vehicle in self.vehicles.values():
            vehicle.update(player_speed, player_lane, dt)
            
        # Maintain continuous traffic by respawning vehicles
        for vehicle in self.vehicles.values():
            # If vehicle goes too far behind, respawn it ahead
            if vehicle.world_y < player_world_y - 1000:
                vehicle.world_y = player_world_y + random.uniform(1500, 2500)
            # If vehicle goes too far ahead, respawn it behind  
            elif vehicle.world_y > player_world_y + 2000:
                vehicle.world_y = player_world_y - random.uniform(500, 1000)
    
    def draw(self, screen, player_world_y, center_y):
        """Draw all traffic vehicles"""
        if not self.enabled:
            return
            
        for vehicle in self.vehicles.values():
            # Only draw vehicles that are visible on screen
            screen_y = vehicle.get_screen_pos(player_world_y, center_y)
            if -100 < screen_y < WINDOW_HEIGHT + 100:
                vehicle.draw(screen, player_world_y, center_y)
    
    def get_debug_info(self):
        """Get debug information about the traffic system"""
        if not self.enabled or not self.vehicles:
            return f"Traffic: OFF (Press T to enable)"
        
        visible_count = 0
        for vehicle in self.vehicles.values():
            # Count vehicles that are near the player
            if abs(vehicle.world_y) < 2000:
                visible_count += 1
        
        return f"Traffic: ON | Vehicles: {len(self.vehicles)} | Visible: {visible_count} | Frame: {self.current_frame:.1f}/{self.max_frame}"
