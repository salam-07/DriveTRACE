import pygame
import sys
from config import *
from player import Player
from traffic import TrafficManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("DriveTRACE Simulation")
        self.clock = pygame.time.Clock()

        # Load and scale road tile
        self.road_tile = pygame.image.load('Assets/roads/road_tile.jpeg')
        self.road_tile = pygame.transform.smoothscale(self.road_tile, 
                                              (ROAD_TILE_WIDTH, ROAD_TILE_HEIGHT))
        self.road_y_offset = 0

        # Create player and traffic
        self.player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.8)
        self.traffic_manager = TrafficManager()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    self.traffic_manager.toggle()

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        return True

    def update(self):
        self.player.update()
        self.traffic_manager.update()
        
        # Update road scroll position
        self.road_y_offset = (self.road_y_offset + self.player.speed * (1/FPS)) % ROAD_TILE_HEIGHT

    def draw(self):
        self.screen.fill(BLACK)

        # Draw road tiles with scrolling
        for y in range(-1, 2):
            tile_y = y * ROAD_TILE_HEIGHT + self.road_y_offset
            self.screen.blit(self.road_tile, (0, tile_y))

        self.traffic_manager.draw(self.screen)
        self.player.draw(self.screen)
        
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