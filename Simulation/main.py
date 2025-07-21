import pygame
import sys
from config import *
from player import Player
from csv_traffic import CSVTrafficManager
import os

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
                    # End simulation and show feedback screen
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
        # Show a black screen with scrollable white text from ai_feedback.txt
        feedback_path = os.path.join(os.path.dirname(__file__), 'Logs', 'ai_feedback.txt')
        try:
            with open(feedback_path, 'r', encoding='utf-8') as f:
                feedback_text = f.read()
        except Exception as e:
            feedback_text = f"Could not load feedback: {e}"

        pygame.font.init()
        font = pygame.font.SysFont('arial', 28)
        lines = []
        for line in feedback_text.split('\n'):
            # Wrap long lines
            while len(line) > 0:
                # Try to fit as much as possible in one line
                cut = len(line)
                while font.size(line[:cut])[0] > self.screen.get_width() - 40 and cut > 0:
                    cut -= 1
                if cut == 0:
                    break
                lines.append(line[:cut])
                line = line[cut:]

        scroll = 0
        max_scroll = max(0, len(lines) * 36 - self.screen.get_height() + 40)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_UP:
                        scroll = max(0, scroll - 36)
                    elif event.key == pygame.K_DOWN:
                        scroll = min(max_scroll, scroll + 36)
            self.screen.fill((0, 0, 0))
            y = 20 - scroll
            for line in lines:
                text_surface = font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (20, y))
                y += 36
            # Draw instructions
            instr_font = pygame.font.SysFont('arial', 20)
            instr = "UP/DOWN to scroll, ESC or Q to exit"
            instr_surface = instr_font.render(instr, True, (200, 200, 200))
            self.screen.blit(instr_surface, (20, self.screen.get_height() - 30))
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