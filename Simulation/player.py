import pygame
import math
from config import *

class Player:
    def __init__(self, x, y):
        self.original_image = pygame.image.load('Assets/vehicles/car_16.png').convert_alpha()
        # Smooth scaling for anti-aliasing
        new_width = int(LANE_WIDTH * VEHICLE_SCALE)
        new_height = int((new_width / self.original_image.get_width()) * self.original_image.get_height())
        self.original_image = pygame.transform.smoothscale(self.original_image, (new_width, new_height))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.lane = LANE_COUNT // 2  # Start in the center lane
        self.target_lane = self.lane
        self.lane_pos = float(self.lane)
        self.lane_changing = False
        self.angle = 0
        self.speed = 0
        self.target_speed = 0
        self.acceleration = 0
        self.turning = 0
        self.last_keys = None
        self.world_y = 0  # Player's world position (centered)

    def handle_input(self, keys):
        # Speed control with number keys
        for i in range(10):
            if keys[getattr(pygame, f'K_{i}')]:
                self.target_speed = (i / 9) * MAX_SPEED

        # Lane change logic: only trigger on key press, not hold
        if self.last_keys is None:
            self.last_keys = keys
        if keys[pygame.K_LEFT] and not self.last_keys[pygame.K_LEFT] and self.target_lane > 0 and not self.lane_changing:
            self.target_lane -= 1
            self.lane_changing = True
            self.turning = 1
        elif keys[pygame.K_RIGHT] and not self.last_keys[pygame.K_RIGHT] and self.target_lane < LANE_COUNT - 1 and not self.lane_changing:
            self.target_lane += 1
            self.lane_changing = True
            self.turning = -1
        self.last_keys = keys

    def update(self):
        # Update speed with smooth acceleration
        speed_diff = self.target_speed - self.speed
        if abs(speed_diff) > 0:
            self.acceleration = (speed_diff / abs(speed_diff)) * ACCELERATION_RATE
            self.speed += self.acceleration * (1/FPS)
            self.speed = max(MIN_SPEED, min(MAX_SPEED, self.speed))
        else:
            self.acceleration = 0

        # Move player in world
        self.world_y += self.speed * (1/FPS)

        # Lane change animation
        if self.lane_changing:
            lane_delta = self.target_lane - self.lane_pos
            move_step = min(abs(lane_delta), 4 * (1/FPS)) * (1 if lane_delta > 0 else -1)
            self.lane_pos += move_step
            # Tilt car during lane change
            self.angle = -20 * self.turning * (1 - abs(self.target_lane - self.lane_pos))
            if abs(self.lane_pos - self.target_lane) < 0.05:
                self.lane_pos = self.target_lane
                self.lane = self.target_lane
                self.lane_changing = False
                self.angle = 0
                self.turning = 0
        else:
            self.angle *= 0.8  # Smoothly return to straight

    def get_lane(self):
        return int(round(self.lane_pos))

    def draw(self, screen, center_x, center_y):
        # Draw player at the center of the screen
        base_x = int((self.lane_pos + 0.5) * LANE_WIDTH)
        base_y = center_y
        self.rect.centerx = base_x
        self.rect.centery = base_y

        # Rotate image with anti-aliasing
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        new_rect = self.image.get_rect(center=self.rect.center)
        self.rect = new_rect

        screen.blit(self.image, self.rect)