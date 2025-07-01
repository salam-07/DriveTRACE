import pygame
import random
import os
from config import *

class TrafficVehicle:
    def __init__(self, lane, world_y, speed=None):
        vehicle_files = [f for f in os.listdir(TRAFFIC_ASSET_DIR) 
                        if f.startswith('car_')]
        vehicle_image = random.choice(vehicle_files)
        self.original_image = pygame.image.load(f'{TRAFFIC_ASSET_DIR}/{vehicle_image}').convert_alpha()
        new_width = int(LANE_WIDTH * VEHICLE_SCALE)
        new_height = int((new_width / self.original_image.get_width()) * self.original_image.get_height())
        self.original_image = pygame.transform.smoothscale(self.original_image, (new_width, new_height))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.lane = lane
        self.world_y = world_y
        self.speed = speed if speed is not None else random(TRAFFIC_SPEED_RANGE[0], TRAFFIC_SPEED_RANGE[1])
        self.is_player_lane = False

    def update(self, player_speed, player_lane):
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
        self.spawn_distance = 4000
        self.despawn_distance = 2000

    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled and not self.vehicles:
            self.spawn_default_traffic()

    def spawn_default_traffic(self):
        self.vehicles = []
        min_gap = 5
        for lane in range(LANE_COUNT):
            for i in range(TRAFFIC_DENSITY):
                world_y = random.uniform(-2000, 4000)
                speed = random.uniform(TRAFFIC_SPEED_RANGE[0], TRAFFIC_SPEED_RANGE[1])
                self.vehicles.append(TrafficVehicle(lane, world_y, speed))

    def update(self, player_speed, player_lane, player_world_y):
        if self.enabled:
            for vehicle in self.vehicles:
                vehicle.update(player_speed, player_lane)
            for vehicle in self.vehicles:
                if vehicle.world_y < player_world_y - self.despawn_distance:
                    vehicle.world_y = player_world_y + self.spawn_distance
                    vehicle.speed = random.uniform(TRAFFIC_SPEED_RANGE[0], TRAFFIC_SPEED_RANGE[1])

    def draw(self, screen, player_world_y, center_y):
        if self.enabled:
            for vehicle in self.vehicles:
                vehicle.draw(screen, player_world_y, center_y)