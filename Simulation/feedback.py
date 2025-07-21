import pygame
import time
import datetime
import os
import csv

# Feedback thresholds (tune as needed)

SLOW_SPEED_THRESHOLD = 150  # km/h or game units per second
STOPPED_SPEED_THRESHOLD = 1  # below this is considered stopped
OVERSPEED_THRESHOLD = 250   # km/h or game units per second (set as needed)

# Colors for warnings

MILD_WARNING_COLOR = (255, 215, 0)   # Gold
HIGH_WARNING_COLOR = (255, 0, 0)     # Red
OVERSPEED_COLOR = (255, 69, 0)       # OrangeRed
INFO_COLOR = (0, 150, 255)           # Blue for informational messages

import time

SWERVE_TIME_THRESHOLD = 1.0  # seconds
SWERVE_MOVEMENT_THRESHOLD = 1  # minimum movement per frame to count as swerving
PROXIMITY_WARNING_DISTANCE = 250  # distance in pixels to trigger proximity warning
COLLISION_DISTANCE = 100  # distance in pixels to trigger collision warning
TRAFFIC_NOTIFICATION_DURATION = 3.0  # seconds to show traffic notification


class FeedbackHUD:
    def __init__(self, font_size=24):  # Reduced from 36 to 24
        pygame.font.init()
        # Try to use a system font for better readability
        try:
            self.font = pygame.font.SysFont('Arial', font_size, bold=False)  # Less bold
            self.bold_font = pygame.font.SysFont('Arial', font_size, bold=True)  # Reduced size difference
        except:
            # Fallback to default font if system font isn't available
            self.font = pygame.font.Font(None, font_size)
            self.bold_font = pygame.font.Font(None, font_size + 2)  # Reduced size difference
        
        self.mild_warning = None
        self.high_warning = None
        self.overspeed_warning = None
        self.swerve_warning = None
        self.proximity_warning = None
        self.collision_warning = None
        self.traffic_notification = None
        self.warning_timer = 0
        self._last_x = None
        self._traffic_notification_start = None
        self._swerve_start_time = None
        self._swerve_active = False
        self._stable_frames = 0
        
        # Warning logging system
        self._setup_warning_log()
        self._last_warnings = set()  # Track previous warnings to avoid duplicates

    def _setup_warning_log(self):
        """Initialize the warning log file"""
        self.log_dir = os.path.join(os.path.dirname(__file__), "Logs")
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        self.log_file_path = os.path.join(self.log_dir, "driving_warnings.csv")
        
        # Create new log file (overwrite existing)
        with open(self.log_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Warning_Type', 'Warning_Message', 'Player_Speed', 'Player_X', 'Player_Y'])

    def _log_warning(self, warning_type, warning_message, speed=None, player_x=None, player_y=None):
        """Log a warning to the CSV file"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Include milliseconds
        
        try:
            with open(self.log_file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, warning_type, warning_message, speed, player_x, player_y])
        except Exception as e:
            print(f"Error logging warning: {e}")

    def _draw_hud_warning(self, surface, text, color, y_pos):
        """Draw a modern HUD-style warning with translucent background and styling"""
        # Render text with antialiasing for better readability
        text_surface = self.bold_font.render(text, True, (255, 255, 255))
        
        # Calculate dimensions with smaller, more aesthetic padding
        padding_x = 16  # Reduced from 30
        padding_y = 8   # Reduced from 15
        total_width = text_surface.get_width() + (padding_x * 2)
        total_height = text_surface.get_height() + (padding_y * 2)
        
        # Center position
        x_pos = (surface.get_width() - total_width) // 2
        
        # Create translucent background surface with more subtle styling
        bg_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
        
        # Draw background with more subtle opacity for aesthetic appeal
        bg_color = (*color[:3], 100)  # More subtle background
        border_color = (*color[:3], 180)  # Softer border
        
        # Smaller, more subtle shadow effect
        shadow_offset = 2  # Reduced from 3
        shadow_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 40), (shadow_offset, shadow_offset, total_width, total_height), border_radius=6)  # Smaller radius
        surface.blit(shadow_surface, (x_pos, y_pos))
        
        # Main background with smaller border radius for sleeker look
        pygame.draw.rect(bg_surface, bg_color, (0, 0, total_width, total_height), border_radius=6)
        
        # Thinner, more elegant border
        pygame.draw.rect(bg_surface, border_color, (0, 0, total_width, total_height), width=2, border_radius=6)
        
        # Smaller top highlight line for subtle HUD effect
        highlight_color = (*color[:3], 200)  # Less intense highlight
        pygame.draw.rect(bg_surface, highlight_color, (2, 2, total_width-4, 2), border_radius=1)  # Thinner highlight
        
        # Blit background to main surface
        surface.blit(bg_surface, (x_pos, y_pos))
        
        # Draw text centered
        text_x = x_pos + padding_x
        text_y = y_pos + padding_y
        
        # Subtler text shadow for better readability
        shadow_surface = self.bold_font.render(text, True, (0, 0, 0))
        surface.blit(shadow_surface, (text_x + 1, text_y + 1))  # Smaller shadow offset
        
        # Draw main text
        surface.blit(text_surface, (text_x, text_y))
        
        return total_height + 12  # Reduced spacing between warnings for more compact layout

    def show_traffic_enabled_notification(self):
        """Show a notification that traffic has been enabled"""
        self.traffic_notification = "Traffic Enabled"
        self._traffic_notification_start = time.time()

    def update(self, speed, player_x=None, player_y=None, traffic_vehicles=None):
        """
        Update feedback messages based on current speed, position, and traffic.
        :param speed: Current speed of the player (float/int)
        :param player_x: Current x position of the player (float/int)
        :param player_y: Current y position of the player (float/int)
        :param traffic_vehicles: List of traffic vehicles with positions
        """
        self.mild_warning = None
        self.high_warning = None
        self.overspeed_warning = None
        self.swerve_warning = None
        self.proximity_warning = None
        self.collision_warning = None
        
        now = time.time()
        
        # Check if traffic notification should be cleared
        if self.traffic_notification and self._traffic_notification_start:
            if now - self._traffic_notification_start > TRAFFIC_NOTIFICATION_DURATION:
                self.traffic_notification = None
                self._traffic_notification_start = None
        
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
        
        # Proximity and collision detection to traffic vehicles
        if player_x is not None and player_y is not None and traffic_vehicles:
            for vehicle in traffic_vehicles:
                # Calculate distance between player and traffic vehicle
                dx = player_x - vehicle.world_x
                dy = player_y - vehicle.world_y
                distance = (dx**2 + dy**2)**0.5
                
                if distance < COLLISION_DISTANCE:
                    self.collision_warning = "COLLISION! Vehicle contact detected!"
                    break  # Collision takes priority over proximity
                elif distance < PROXIMITY_WARNING_DISTANCE:
                    self.proximity_warning = "Too close to traffic! Maintain safe distance."
                    # Don't break here in case there's a closer collision
        
        if speed < STOPPED_SPEED_THRESHOLD:
            self.high_warning = "Stopped: Safely pull over to the left if you want to stop."
        elif speed < SLOW_SPEED_THRESHOLD:
            self.mild_warning = "Driving slow on highways isn't safe."
        if speed > OVERSPEED_THRESHOLD:
            self.overspeed_warning = "Overspeeding! Slow down to avoid accidents."
        
        # Log any active warnings
        self._log_active_warnings(speed, player_x, player_y)

    def _log_active_warnings(self, speed, player_x, player_y):
        """Log all currently active warnings to avoid duplicate logging"""
        current_warnings = set()
        
        # Collect all active warnings
        warnings_to_check = [
            ('COLLISION', self.collision_warning),
            ('PROXIMITY', self.proximity_warning),
            ('SWERVING', self.swerve_warning),
            ('STOPPED', self.high_warning),
            ('SLOW_DRIVING', self.mild_warning),
            ('OVERSPEEDING', self.overspeed_warning)
        ]
        
        for warning_type, warning_message in warnings_to_check:
            if warning_message:
                current_warnings.add(warning_type)
                # Only log if this is a new warning (not logged recently)
                if warning_type not in self._last_warnings:
                    self._log_warning(warning_type, warning_message, speed, player_x, player_y)
        
        # Update the set of last warnings
        self._last_warnings = current_warnings

    def draw(self, surface):
        y = 30  # Start higher for better positioning with smaller warnings
        
        # Informational notifications first (blue)
        if self.traffic_notification:
            y += self._draw_hud_warning(surface, self.traffic_notification, INFO_COLOR, y)
        
        # Critical warnings first (red - highest priority)
        if self.collision_warning:
            y += self._draw_hud_warning(surface, self.collision_warning, HIGH_WARNING_COLOR, y)
        
        # High priority warnings (red)
        if self.high_warning:
            y += self._draw_hud_warning(surface, self.high_warning, HIGH_WARNING_COLOR, y)
        
        if self.proximity_warning:
            y += self._draw_hud_warning(surface, self.proximity_warning, MILD_WARNING_COLOR, y)
        
        if self.swerve_warning:
            y += self._draw_hud_warning(surface, self.swerve_warning, HIGH_WARNING_COLOR, y)
        
        # Medium priority warnings (orange)
        if self.overspeed_warning:
            y += self._draw_hud_warning(surface, self.overspeed_warning, OVERSPEED_COLOR, y)
        
        # Low priority warnings (yellow)
        if self.mild_warning:
            y += self._draw_hud_warning(surface, self.mild_warning, MILD_WARNING_COLOR, y)
