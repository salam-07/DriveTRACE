import pygame

# Feedback thresholds (tune as needed)

SLOW_SPEED_THRESHOLD = 150  # km/h or game units per second
STOPPED_SPEED_THRESHOLD = 1  # below this is considered stopped
OVERSPEED_THRESHOLD = 250   # km/h or game units per second (set as needed)

# Colors for warnings

MILD_WARNING_COLOR = (255, 215, 0)   # Gold
HIGH_WARNING_COLOR = (255, 0, 0)     # Red
OVERSPEED_COLOR = (255, 69, 0)       # OrangeRed

class FeedbackHUD:
    def __init__(self, font_size=32):
        pygame.font.init()
        self.font = pygame.font.Font(None, font_size)
        self.mild_warning = None
        self.high_warning = None
        self.overspeed_warning = None
        self.warning_timer = 0

    def update(self, speed):
        """
        Update feedback messages based on current speed.
        :param speed: Current speed of the player (float/int)
        """
        self.mild_warning = None
        self.high_warning = None
        self.overspeed_warning = None
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
        if self.mild_warning:
            text_surface = self.font.render(self.mild_warning, True, MILD_WARNING_COLOR)
            rect = text_surface.get_rect(center=(surface.get_width()//2, y))
            surface.blit(text_surface, rect)
