import pygame
import random
import os
from config import *

class TrafficVehicle:
    def __init__(self, lane, y_pos):
        # Load random vehicle image (excluding car_17.png which is player's car)
        vehicle_files = [f for f in os.listdir('Assets/vehicles') 
                        if f.startswith('car_') and f != 'car_17.png']
        vehicle_image = random.choice(vehicle_files)
        self.original_image = pygame.image.load(f'Assets/vehicles/{vehicle_image}')
        
        # Scale the image
        new_width = int(LANE_WIDTH * VEHICLE_SCALE)
        new_height = int((new_width / self.original_image.get_width()) * self.original_image.get_height())
        self.image = pygame.transform.smoothscale(self.original_image, (new_width, new_height))
        
        # Position the vehicle
        self.rect = self.image.get_rect()
        self.lane = lane
        self.rect.centerx = (lane + 0.5) * LANE_WIDTH
        self.rect.centery = y_pos
        
        # Set random speed within range
        self.speed = random.uniform(TRAFFIC_SPEED_RANGE[0], TRAFFIC_SPEED_RANGE[1])

    def update(self):
        # Move vehicle downward
        self.rect.y += self.speed * (1/FPS)
        
        # Reset position if vehicle goes off screen
        if self.rect.top > WINDOW_HEIGHT:
            self.rect.bottom = 0
            # Optionally change lane when resetting
            self.lane = random.randint(0, LANE_COUNT - 1)
            self.rect.centerx = (self.lane + 0.5) * LANE_WIDTH

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class TrafficManager:
    def __init__(self):
        self.vehicles = []
        self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled and not self.vehicles:
            self.spawn_initial_vehicles()

    def spawn_initial_vehicles(self):
        # Spawn one vehicle per lane at random positions
        for lane in range(LANE_COUNT):
            y_pos = random.randint(-WINDOW_HEIGHT, WINDOW_HEIGHT)
            self.vehicles.append(TrafficVehicle(lane, y_pos))

    def update(self):
        if self.enabled:
            for vehicle in self.vehicles:
                vehicle.update()

    def draw(self, screen):
        if self.enabled:
            for vehicle in self.vehicles:
                vehicle.draw(screen)