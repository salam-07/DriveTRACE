
import pygame
import sys
import os
import time
from config import *
from player import Player
from csv_traffic import CSVTrafficManager
from feedback import FeedbackHUD
from pause_menu import PauseMenu
from feedback_screen import FeedbackScreen
from ending_screen import EndingScreen
from renderer import Renderer
from input_handler import InputHandler
from sound_manager import SoundManager

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

        # Create game components
        self.player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.8)
        self.traffic_manager = CSVTrafficManager()
        self.feedback_hud = FeedbackHUD()
        
        # Create modular components
        self.pause_menu = PauseMenu()
        self.feedback_screen = FeedbackScreen()
        self.ending_screen = EndingScreen()
        self.renderer = Renderer(self.screen)
        self.input_handler = InputHandler()
        self.sound_manager = SoundManager()
        self.game_ended = False
        self.collision_detected = False
        self.collision_start_time = 0
        self.collision_delay = 2.0  # 2 seconds delay

    def change_road(self, road_number):
        """Change the road texture to a different one"""
        import os
        road_path = os.path.join(os.path.dirname(__file__), "Assets", "roads", f"road_tile_{road_number}.jpeg")
        
        # Fallback to default road if file doesn't exist
        if not os.path.exists(road_path):
            road_path = ROAD_ASSET_DIR
            
        self.road_tile = pygame.image.load(road_path)
        self.road_tile = pygame.transform.smoothscale(self.road_tile, 
                                              (ROAD_TILE_WIDTH, ROAD_TILE_HEIGHT))

    def update(self):
        if self.input_handler.paused:
            return  # Don't update anything when paused
        
        if self.game_ended:
            return  # Don't update anything when game has ended
            
        # Handle collision timing
        if self.collision_detected:
            if time.time() - self.collision_start_time >= self.collision_delay:
                self.game_ended = True
            return  # Don't update other game elements during collision delay
            
        self.player.update()
        self.traffic_manager.update(self.player.speed, self.player.get_lane(), self.player.world_y)
        
        # Get traffic vehicles for proximity detection
        traffic_vehicles = list(self.traffic_manager.vehicles.values()) if hasattr(self.traffic_manager, 'vehicles') else []
        
        # Update feedback HUD with current speed, position, and traffic data
        self.feedback_hud.update(
            self.player.speed, 
            player_x=self.player.x, 
            player_y=self.player.world_y,
            traffic_vehicles=traffic_vehicles,
            sound_manager=self.sound_manager
        )
        
        # Check if collision occurred and start the delay
        if self.feedback_hud.collision_occurred and not self.collision_detected:
            self.player.stop_vehicle()
            self.collision_detected = True
            self.collision_start_time = time.time()
        
        # Update sounds
        traffic_enabled = getattr(self.traffic_manager, 'enabled', False)
        self.sound_manager.update(traffic_enabled)

        # Update road scroll position (now based on player world_y)
        self.road_y_offset = self.player.world_y % ROAD_TILE_HEIGHT

    def draw(self):
        # Draw background
        self.renderer.draw_background(self.road_tile, self.road_y_offset)
        
        # Draw game objects
        self.renderer.draw_game_objects(
            self.traffic_manager, 
            self.player, 
            self.feedback_hud, 
            self.player.world_y
        )
        
        # Draw pause menu if paused
        if self.input_handler.paused:
            self.pause_menu.draw(self.screen)
        
        # Draw ending screen if game has ended
        if self.game_ended:
            self.ending_screen.draw(self.screen)
        
        # Finalize frame
        self.renderer.finalize_frame()

    def run(self):
        running = True
        while running:
            # Handle input
            result = self.input_handler.handle_events(
                self.pause_menu, 
                self.feedback_screen, 
                self.clock, 
                self.screen,
                self.sound_manager,
                self.player,
                self
            )
            
            if result == False:
                running = False
            elif result == 'toggle_traffic':
                # Check if traffic was disabled before toggling
                was_disabled = not getattr(self.traffic_manager, 'enabled', False)
                self.traffic_manager.toggle()
                # Show notification if traffic was just enabled
                if was_disabled and getattr(self.traffic_manager, 'enabled', False):
                    self.feedback_hud.show_traffic_enabled_notification()
            
            # Handle continuous input for player movement
            keys = self.input_handler.get_continuous_input(self)
            if keys:
                self.player.handle_input(keys)
            
            # Update and draw
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()