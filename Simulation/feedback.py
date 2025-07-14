import pygame

# Feedback thresholds (tune as needed)

SLOW_SPEED_THRESHOLD = 150  # km/h or game units per second
STOPPED_SPEED_THRESHOLD = 1  # below this is considered stopped
OVERSPEED_THRESHOLD = 250   # km/h or game units per second (set as needed)

# Colors for warnings

MILD_WARNING_COLOR = (255, 215, 0)   # Gold
HIGH_WARNING_COLOR = (255, 0, 0)     # Red
OVERSPEED_COLOR = (255, 69, 0)       # OrangeRed

import time

SWERVE_TIME_THRESHOLD = 1.0  # seconds
SWERVE_MOVEMENT_THRESHOLD = 2  # minimum movement per frame to count as swerving


class FeedbackHUD:
    def __init__(self, font_size=32):
        pygame.font.init()
        self.font = pygame.font.Font(None, font_size)
        self.mild_warning = None
        self.high_warning = None
        self.overspeed_warning = None
        self.swerve_warning = None
        self.warning_timer = 0
        self._last_x = None
        self._swerve_start_time = None
        self._swerve_active = False
        self._stable_frames = 0

    def update(self, speed, player_x=None):
        """
        Update feedback messages based on current speed and x position.
        :param speed: Current speed of the player (float/int)
        :param player_x: Current x position of the player (float/int)
        """
        self.mild_warning = None
        self.high_warning = None
        self.overspeed_warning = None
        self.swerve_warning = None
        
        now = time.time()
        
        # Swerve detection
        if player_x is not None and self._last_x is not None:
            x_movement = abs(player_x - self._last_x)
            
            if x_movement > SWERVE_MOVEMENT_THRESHOLD:
                # Player is moving laterally significantly
                if not self._swerve_active:
                    self._swerve_start_time = now
                    self._swerve_active = True
                    self._stable_frames = 0
                elif now - self._swerve_start_time > SWERVE_TIME_THRESHOLD:
                    self.swerve_warning = "Swerving detected! Please keep your lane on highways."
            else:
                # Player not moving much laterally
                self._stable_frames += 1
                # Reset swerve detection after a few stable frames
                if self._stable_frames > 5:
                    self._swerve_active = False
                    self._swerve_start_time = None
                    self._stable_frames = 0
        
        if player_x is not None:
            self._last_x = player_x
        
        if speed < STOPPED_SPEED_THRESHOLD:
            self.high_warning = "Stopped: Safely pull over to the left if you want to stop."
        elif speed < SLOW_SPEED_THRESHOLD:
            self.mild_warning = "Driving slow on highways isn't safe."
        if speed > OVERSPEED_THRESHOLD:
            self.overspeed_warning = "Overspeeding! Slow down to avoid accidents."

    def draw(self, surface):
        y = 40
        if self.high_warning:
            text_surface = self.font.render(self.high_warning, True, HIGH_WARNING_COLOR)
            rect = text_surface.get_rect(center=(surface.get_width()//2, y))
            surface.blit(text_surface, rect)
            y += 50
        if self.overspeed_warning:
            text_surface = self.font.render(self.overspeed_warning, True, OVERSPEED_COLOR)
            rect = text_surface.get_rect(center=(surface.get_width()//2, y))
            surface.blit(text_surface, rect)
            y += 50
        if self.swerve_warning:
            text_surface = self.font.render(self.swerve_warning, True, HIGH_WARNING_COLOR)
            rect = text_surface.get_rect(center=(surface.get_width()//2, y))
            surface.blit(text_surface, rect)
            y += 50
        if self.mild_warning:
            text_surface = self.font.render(self.mild_warning, True, MILD_WARNING_COLOR)
            rect = text_surface.get_rect(center=(surface.get_width()//2, y))
            surface.blit(text_surface, rect)
