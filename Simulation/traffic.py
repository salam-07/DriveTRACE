import pygame
import random
import os
from config import *
from traffic_data_loader import load_traffic_data

class TrafficVehicle:
    def __init__(self, lane, world_y, speed):
        vehicle_files = [f for f in os.listdir('Assets/vehicles') 
                        if f.startswith('car_') and f != 'car_17.png']
        vehicle_image = random.choice(vehicle_files)
        self.original_image = pygame.image.load(f'Assets/vehicles/{vehicle_image}').convert_alpha()
        new_width = int(LANE_WIDTH * VEHICLE_SCALE)
        new_height = int((new_width / self.original_image.get_width()) * self.original_image.get_height())
        self.original_image = pygame.transform.smoothscale(self.original_image, (new_width, new_height))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.lane = lane
        self.world_y = world_y
        self.speed = speed
        self.is_player_lane = False

    def update(self, player_speed, player_lane):
        if self.lane == player_lane:
            self.is_player_lane = True
            self.speed += (player_speed - self.speed) * 0.1
        else:
            self.is_player_lane = False
        self.world_y -= (player_speed - self.speed) * (1/FPS)

    def get_screen_pos(self, player_world_y, center_y):
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
        self.traffic_data = load_traffic_data()
        self.spawn_distance = 4000
        self.despawn_distance = 2000

    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled and not self.vehicles:
            self.spawn_vehicles_from_data()

    def spawn_vehicles_from_data(self):
        self.vehicles = []
        # Only spawn vehicles within a window around the player's starting world_y
        player_start_y = 0
        window = 2000  # Only spawn vehicles within ±2000 units
        count = 0
        for entry in self.traffic_data:
            world_y = entry['world_y']
            if player_start_y - window <= world_y <= player_start_y + window:
                lane = entry['lane']
                speed = entry['speed']
                self.vehicles.append(TrafficVehicle(lane, world_y, speed))
                count += 1
            if count > 100:  # Hard cap to prevent overload
                break

    def update(self, player_speed, player_lane, player_world_y):
        if self.enabled:
            for vehicle in self.vehicles:
                vehicle.update(player_speed, player_lane)
            # Despawn and respawn vehicles far ahead/behind
            for vehicle in self.vehicles:
                if vehicle.world_y < player_world_y - self.despawn_distance:
                    # Respawn at max world_y from CSV + offset
                    max_y = max(v.world_y for v in self.vehicles)
                    vehicle.world_y = max_y + 100

    def draw(self, screen, player_world_y, center_y):
        if self.enabled:
            for vehicle in self.vehicles:
                vehicle.draw(screen, player_world_y, center_y)