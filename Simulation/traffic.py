import pygame
import random
import os
from config import *

class TrafficVehicle:
    def __init__(self, lane, world_y, speed=None):
        # Load random vehicle image (excluding car_17.png which is player's car)
        vehicle_files = [f for f in os.listdir('Assets/vehicles') 
                        if f.startswith('car_') and f != 'car_17.png']
        vehicle_image = random.choice(vehicle_files)
        self.original_image = pygame.image.load(f'Assets/vehicles/{vehicle_image}').convert_alpha()
        # Smooth scaling for anti-aliasing
        new_width = int(LANE_WIDTH * VEHICLE_SCALE)
        new_height = int((new_width / self.original_image.get_width()) * self.original_image.get_height())
        self.original_image = pygame.transform.smoothscale(self.original_image, (new_width, new_height))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.lane = lane
        self.world_y = world_y
        # Set random speed within range, or use provided
        self.speed = speed if speed is not None else random.uniform(TRAFFIC_SPEED_RANGE[0], TRAFFIC_SPEED_RANGE[1])
        self.is_player_lane = False

    def update(self, player_speed, player_lane):
        # If in player's lane, blend speed toward player speed for realism
        if self.lane == player_lane:
            self.is_player_lane = True
            self.speed += (player_speed - self.speed) * 0.1
        else:
            self.is_player_lane = False
        self.world_y += self.speed * (1/FPS)

    def get_screen_pos(self, player_world_y, center_y):
        # Calculate screen y based on world position relative to player
        return int(center_y - (self.world_y - player_world_y))

    def draw(self, screen, player_world_y, center_y):
        base_x = int((self.lane + 0.5) * LANE_WIDTH)
        base_y = self.get_screen_pos(player_world_y, center_y)
        self.rect.centerx = base_x
        self.rect.centery = base_y
        screen.blit(self.image, self.rect)

class TrafficManager:
    def __init__(self):
        self.vehicles = []
        self.enabled = False
        self.spawn_distance = 2000  # How far ahead to spawn traffic
        self.despawn_distance = 1000  # How far behind player to despawn

    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled and not self.vehicles:
            self.spawn_initial_vehicles(0)

    def spawn_initial_vehicles(self, player_world_y):
        # Spawn vehicles in each lane, spaced apart to avoid overlap
        self.vehicles = []
        min_gap = 120  # Minimum vertical gap between vehicles
        for lane in range(LANE_COUNT):
            y_positions = [player_world_y + i * min_gap for i in range(-10, 20)]
            random.shuffle(y_positions)
            for i in range(6):  # 6 vehicles per lane
                world_y = y_positions[i]
                speed = random.uniform(TRAFFIC_SPEED_RANGE[0], TRAFFIC_SPEED_RANGE[1])
                self.vehicles.append(TrafficVehicle(lane, world_y, speed))

    def update(self, player_speed, player_lane, player_world_y):
        if self.enabled:
            for vehicle in self.vehicles:
                vehicle.update(player_speed, player_lane)
            # Prevent overlap in world coordinates
            for lane in range(LANE_COUNT):
                lane_vehicles = [v for v in self.vehicles if v.lane == lane]
                lane_vehicles.sort(key=lambda v: v.world_y)
                for i in range(1, len(lane_vehicles)):
                    prev = lane_vehicles[i-1]
                    curr = lane_vehicles[i]
                    if curr.world_y - prev.world_y < 60:
                        curr.world_y = prev.world_y + 60
            # Despawn and respawn vehicles far ahead/behind
            for vehicle in self.vehicles:
                if vehicle.world_y < player_world_y - self.despawn_distance:
                    vehicle.world_y = player_world_y + self.spawn_distance
                    vehicle.speed = random.uniform(TRAFFIC_SPEED_RANGE[0], TRAFFIC_SPEED_RANGE[1])

    def draw(self, screen, player_world_y, center_y):
        if self.enabled:
            for vehicle in self.vehicles:
                vehicle.draw(screen, player_world_y, center_y)