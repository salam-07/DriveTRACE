
import pygame
import sys
from config import *
from player import Player
from csv_traffic import CSVTrafficManager
import os
from ai_feedback import generate_and_save_feedback
# Import FeedbackHUD
from feedback import FeedbackHUD

ICON_PATH = os.path.join(os.path.dirname(__file__), "Assets/ui/logo3.png")

class Game:
    def __init__(self):
        pygame.init()
        icon = pygame.image.load(ICON_PATH)
        pygame.display.set_icon(icon)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption("DriveTRACE Simulation")

        self.clock = pygame.time.Clock()

        # Load and scale road tile
        self.road_tile = pygame.image.load(ROAD_ASSET_DIR)
        self.road_tile = pygame.transform.smoothscale(self.road_tile, 
                                              (ROAD_TILE_WIDTH, ROAD_TILE_HEIGHT))
        self.road_y_offset = 0

        # Create player and traffic
        self.player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.8)
        self.traffic_manager = CSVTrafficManager()

        # Feedback HUD
        self.feedback_hud = FeedbackHUD()

        # Traffic and ignition sounds
        from sounds import TrafficSound, IgnitionSound, CarSound
        self.traffic_sound = TrafficSound()
        self.ignition_sound = IgnitionSound()
        self.car_sound = CarSound()
        self.ignition_sound.play(loops=0)
        self.car_sound_timer = pygame.time.get_ticks() + 4000  # 4 seconds after ignition
        self.car_sound_started = False

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return False
                if event.key == pygame.K_e:
                    # Generate feedback before showing feedback screen
                    generate_and_save_feedback()
                    self.show_feedback_screen()
                    return False
                if event.key == pygame.K_t:
                    # Check if traffic was disabled before toggling
                    was_disabled = not getattr(self.traffic_manager, 'enabled', False)
                    self.traffic_manager.toggle()
                    # Show notification if traffic was just enabled
                    if was_disabled and getattr(self.traffic_manager, 'enabled', False):
                        self.feedback_hud.show_traffic_enabled_notification()

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        return True

    def show_feedback_screen(self):
        # Show a black screen with scrollable white text from ai_feedback.txt, improved readability
        feedback_path = os.path.join(os.path.dirname(__file__), 'Logs', 'ai_feedback.txt')
        try:
            with open(feedback_path, 'r', encoding='utf-8') as f:
                feedback_text = f.read()
        except Exception as e:
            feedback_text = f"Could not load feedback: {e}"

        pygame.font.init()
        font = pygame.font.SysFont('consolas', 24)  # Monospace font for better readability
        line_spacing = 8
        text_color = (240, 240, 240)  # Slightly softer white
        bg_color = (15, 15, 20)  # Dark blue-ish background
        text_bg_color = (15, 15, 20)  # Semi-transparent dark background for text area
        margin_x = 100
        margin_y = 60
        max_width = min(1000, self.screen.get_width() - 2 * margin_x)  # Limit line length for readability

        # Word wrap for better readability with optimal line length
        def wrap_text(text, font, max_width):
            words = text.split()
            lines = []
            current_line = ''
            for word in words:
                test_line = current_line + (' ' if current_line else '') + word
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                        current_line = word
                    else:
                        # Handle very long words
                        lines.append(word)
            if current_line:
                lines.append(current_line)
            return lines

        # Split feedback into paragraphs, then wrap each
        lines = []
        for para in feedback_text.split('\n'):
            if para.strip() == '':
                lines.append('')
            else:
                lines.extend(wrap_text(para, font, max_width))

        line_height = font.get_height() + line_spacing
        scroll = 0
        max_scroll = max(0, len(lines) * line_height - self.screen.get_height() + margin_y)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_UP:
                        scroll = max(0, scroll - line_height)
                    elif event.key == pygame.K_DOWN:
                        scroll = min(max_scroll, scroll + line_height)
            self.screen.fill(bg_color)
            # Draw semi-transparent rectangle for text area with rounded corners effect
            text_area_width = self.screen.get_width() - 2 * margin_x
            text_area_height = self.screen.get_height() - 2 * margin_y
            s = pygame.Surface((text_area_width, text_area_height), pygame.SRCALPHA)
            s.fill(text_bg_color)
            self.screen.blit(s, (margin_x, margin_y))
            
            # Render text with better vertical spacing
            y = margin_y + 30 - scroll
            for line in lines:
                if line.strip() == '':
                    y += line_height // 2
                    continue
                if y > margin_y - line_height and y < self.screen.get_height() - margin_y:  # Only render visible lines
                    text_surface = font.render(line, True, text_color)
                    self.screen.blit(text_surface, (margin_x + 30, y))
                y += line_height
            
            # Draw title and instructions with better styling
            title_font = pygame.font.SysFont('segoeui', 28, bold=True)
            title_text = "AI Driving Instructor Feedback"
            title_surface = title_font.render(title_text, True, (200, 220, 255))
            title_x = (self.screen.get_width() - title_surface.get_width()) // 2
            self.screen.blit(title_surface, (title_x, 20))
            
            instr_font = pygame.font.SysFont('segoeui', 20)
            instr = "UP/DOWN arrows to scroll • ESC or Q to exit"
            instr_surface = instr_font.render(instr, True, (160, 180, 200))
            instr_x = (self.screen.get_width() - instr_surface.get_width()) // 2
            self.screen.blit(instr_surface, (instr_x, self.screen.get_height() - 35))
            pygame.display.flip()
            self.clock.tick(30)

    def update(self):
        self.player.update()
        self.traffic_manager.update(self.player.speed, self.player.get_lane(), self.player.world_y)
        
        # Get traffic vehicles for proximity detection
        traffic_vehicles = list(self.traffic_manager.vehicles.values()) if hasattr(self.traffic_manager, 'vehicles') else []
        
        # Update feedback HUD with current speed, position, and traffic data
        self.feedback_hud.update(
            self.player.speed, 
            player_x=self.player.x, 
            player_y=self.player.world_y,
            traffic_vehicles=traffic_vehicles
        )
        # Play/stop traffic sound based on traffic enabled
        if getattr(self.traffic_manager, 'enabled', False): #checks the enabled attribute of traffic. Default returns False
            if not self.traffic_sound.is_playing():
                #if traffic traffic is enabled and sound is not playing, play it
                self.traffic_sound.play()
        else:
            #if traffic is disabled and sound is playing, stop it
            if self.traffic_sound.is_playing():
                self.traffic_sound.stop()

        #car driving sound
        # Start car sound 4 seconds after ignition
        now = pygame.time.get_ticks()
        #if not already playing and after the set 4 second timer.
        if not self.car_sound_started and now >= self.car_sound_timer:
            self.car_sound.play(loops=-1) #loop infinite times
            self.car_sound_started = True

        # Update road scroll position (now based on player world_y)
        self.road_y_offset = self.player.world_y % ROAD_TILE_HEIGHT

    def draw(self):
        self.screen.fill(BLACK)
        center_y = int(WINDOW_HEIGHT * 0.8)
        # Draw road tiles and scroll them
        for y in range(-3, 3): 
            tile_y = y * ROAD_TILE_HEIGHT + center_y + self.road_y_offset
            self.screen.blit(self.road_tile, (0, tile_y))
        self.traffic_manager.draw(self.screen, self.player.world_y, center_y)
        self.player.draw(self.screen, int(self.player.x), center_y)
        # Draw feedback HUD
        self.feedback_hud.draw(self.screen)
        
        # Draw debug info
        # if hasattr(self.traffic_manager, 'get_debug_info'):
        #     debug_text = self.traffic_manager.get_debug_info()
        #     font = pygame.font.Font(None, 36)
        #     text_surface = font.render(debug_text, True, WHITE)
        #     self.screen.blit(text_surface, (10, 10))
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()