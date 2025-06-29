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
        # Cluster traffic speeds for realism, with some jitter
        base_speed = speed if speed is not None else random.uniform(TRAFFIC_SPEED_RANGE[0], TRAFFIC_SPEED_RANGE[1])
        self.speed = base_speed + random.uniform(-10, 10)
        self.jitter = random.uniform(-2, 2)
        self.is_player_lane = False

    def update(self, player_speed, player_lane):
        # If in player's lane, blend speed toward player speed for realism
        if self.lane == player_lane:
            self.is_player_lane = True
            self.speed += (player_speed - self.speed) * 0.1
        else:
            self.is_player_lane = False
        # Move traffic relative to player (subtract player speed)
        self.world_y -= (player_speed - self.speed + self.jitter) * (1/FPS)

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
        self.spawn_distance = 4000  # Increased spawn range
        self.despawn_distance = 2000  # Increased despawn range

    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled and not self.vehicles:
            self.spawn_initial_vehicles(0)

    def spawn_initial_vehicles(self, player_world_y):
        # Spawn vehicles in each lane, spaced apart to avoid overlap
        self.vehicles = []
        min_gap = 80  # More vehicles, closer together
        for lane in range(LANE_COUNT):
            y_positions = [player_world_y + i * min_gap for i in range(-25, 50)]
            random.shuffle(y_positions)
            for i in range(20):  # 20 vehicles per lane
                world_y = y_positions[i]
                # Cluster some vehicles at similar speeds for realism
                if i % 5 == 0:
                    base_speed = random.uniform(TRAFFIC_SPEED_RANGE[0], TRAFFIC_SPEED_RANGE[1])
                speed = base_speed + random.uniform(-8, 8)
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
                    if curr.world_y - prev.world_y < 50:
                        curr.world_y = prev.world_y + 50
            # Despawn and respawn vehicles far ahead/behind
            for vehicle in self.vehicles:
                if vehicle.world_y < player_world_y - self.despawn_distance:
                    vehicle.world_y = player_world_y + self.spawn_distance
                    vehicle.speed = random.uniform(TRAFFIC_SPEED_RANGE[0], TRAFFIC_SPEED_RANGE[1])

    def draw(self, screen, player_world_y, center_y):
        if self.enabled:
            for vehicle in self.vehicles:
                vehicle.draw(screen, player_world_y, center_y)