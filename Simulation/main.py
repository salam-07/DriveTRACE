import pygame
import sys
from config import *
from player import Player
from csv_traffic import CSVTrafficManager
import os

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

        # Traffic and ignition sounds
        from sounds import TrafficSound, IgnitionSound, CarSound
        self.traffic_sound = TrafficSound()
        self.traffic_sound_playing = False
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    self.traffic_manager.toggle()

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        return True

    def update(self):
        self.player.update()
        self.traffic_manager.update(self.player.speed, self.player.get_lane(), self.player.world_y)
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
        
        # Draw debug info
        if hasattr(self.traffic_manager, 'get_debug_info'):
            debug_text = self.traffic_manager.get_debug_info()
            font = pygame.font.Font(None, 36)
            text_surface = font.render(debug_text, True, WHITE)
            self.screen.blit(text_surface, (10, 10))
        
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