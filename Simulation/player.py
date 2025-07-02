import pygame
import math
from config import *

class Player:
    def __init__(self, x, y):
        #load the car asset and scale to choice
        car_img = pygame.image.load(PLAYER_TILE_ASSET).convert_alpha()
        new_width = int(LANE_WIDTH * VEHICLE_SCALE)
        new_height = int((new_width / car_img.get_width()) * car_img.get_height())
        car_img = pygame.transform.smoothscale(car_img, (new_width, new_height))

        self.original_image = car_img
        self.image = self.original_image
        self.rect = self.image.get_rect()

        self.x = (LANE_COUNT // 2 + 0.5) * LANE_WIDTH
        self.y = 0  # world y
        self.angle = 0  # visual angle
        self.heading = 0  # direction in degrees
        self.speed = 0
        self.target_speed = 0
        self.acceleration = 0
        self.last_keys = None

    def handle_input(self, keys):
        # Speed control with number keys
        for i in range(10):
            #see which numeric key is being pressed
            if keys[getattr(pygame, f'K_{i}')]:
                #linear division of speed from 0 to 9
                self.target_speed = (i / 9) * MAX_SPEED
                
            #implement sudden braking
            if keys[pygame.K_DOWN]:
                self.target_speed = 0
            if keys[pygame.K_x]:
                self.target_speed = 500
        steer = 0
        if keys[pygame.K_LEFT]:
            steer -= 1
        if keys[pygame.K_RIGHT]:
            steer += 1
        self.steer = steer

    def update(self):
        # Update speed with smooth acceleration
        speed_diff = self.target_speed - self.speed
        if abs(speed_diff) > 0:
            self.acceleration = (speed_diff / abs(speed_diff)) * ACCELERATION_RATE
            self.speed += self.acceleration * (1/FPS)
            self.speed = max(MIN_SPEED, min(MAX_SPEED, self.speed))
        else:
            self.acceleration = 0
        # Update heading based on steering and speed
        if self.speed > 5:
            self.heading += self.steer * TURNING_SPEED * (self.speed / MAX_SPEED)
        # Clamp heading to ±45 degrees
        self.heading = max(-45, min(45, self.heading))
        # Use full speed for both x and y (no slowdown when turning)
        rad = math.radians(self.heading)
        dx = math.sin(rad) * self.speed * (1/FPS)
        dy = math.cos(rad) * self.speed * (1/FPS)
        self.x += dx
        self.y += dy
        self.world_y = self.y
        # Clamp to road boundaries
        min_x = self.rect.width // 2
        max_x = WINDOW_WIDTH - self.rect.width // 2
        self.x = max(min_x, min(max_x, self.x))
        # Visual angle for car tilt
        self.angle = -self.steer * TURNING_ANGLE * (self.speed / MAX_SPEED)

    def get_lane(self):
        # Return closest lane index
        return int(self.x // LANE_WIDTH)

    def draw(self, screen, center_x, center_y):
        # Draw player at (self.x, center_y)
        draw_x = int(self.x)
        draw_y = center_y
        self.rect.centerx = draw_x
        self.rect.centery = draw_y
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        new_rect = self.image.get_rect(center=self.rect.center)
        self.rect = new_rect
        screen.blit(self.image, self.rect)