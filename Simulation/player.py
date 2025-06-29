import pygame
import math
from config import *

class Player:
    def __init__(self, x, y):
        self.original_image = pygame.image.load('Assets/vehicles/car_17.png')
        # Scale the image based on lane width
        new_width = int(LANE_WIDTH * VEHICLE_SCALE)
        new_height = int((new_width / self.original_image.get_width()) * self.original_image.get_height())
        self.original_image = pygame.transform.smoothscale(self.original_image, (new_width, new_height))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.angle = 0
        self.speed = 0
        self.target_speed = 0
        self.acceleration = 0

    def handle_input(self, keys):
        # Speed control with number keys
        for i in range(10):
            if keys[getattr(pygame, f'K_{i}')]:
                self.target_speed = (i / 9) * MAX_SPEED

        # Turning control
        if keys[pygame.K_LEFT]:
            self.angle += TURNING_SPEED * (self.speed / MAX_SPEED)
        if keys[pygame.K_RIGHT]:
            self.angle -= TURNING_SPEED * (self.speed / MAX_SPEED)

    def update(self):
        # Update speed with smooth acceleration
        speed_diff = self.target_speed - self.speed
        if abs(speed_diff) > 0:
            self.acceleration = (speed_diff / abs(speed_diff)) * ACCELERATION_RATE
            self.speed += self.acceleration * (1/FPS)
            self.speed = max(MIN_SPEED, min(MAX_SPEED, self.speed))

        # Update position based on speed and angle
        radian_angle = math.radians(self.angle)
        self.rect.x += math.sin(radian_angle) * self.speed * (1/FPS)
        self.rect.y -= math.cos(radian_angle) * self.speed * (1/FPS)

        # Clamp position to stay within the road boundaries
        min_x = self.rect.width // 2
        max_x = WINDOW_WIDTH - self.rect.width // 2
        min_y = self.rect.height // 3
        max_y = WINDOW_HEIGHT - self.rect.height // 2
        self.rect.centerx = max(min_x, min(max_x, self.rect.centerx))
        self.rect.centery = max(min_y, min(max_y, self.rect.centery))

        # Rotate image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        new_rect = self.image.get_rect(center=self.rect.center)
        self.rect = new_rect

    def draw(self, screen):
        screen.blit(self.image, self.rect)