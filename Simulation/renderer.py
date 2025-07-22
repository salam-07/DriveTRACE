import pygame
from config import *

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        
    def draw_background(self, road_tile, road_y_offset):
        """Draw the scrolling road background"""
        self.screen.fill(BLACK)
        center_y = int(WINDOW_HEIGHT * 0.8)
        # Draw road tiles and scroll them
        for y in range(-3, 3): 
            tile_y = y * ROAD_TILE_HEIGHT + center_y + road_y_offset
            self.screen.blit(road_tile, (0, tile_y))
    
    def draw_game_objects(self, traffic_manager, player, feedback_hud, player_world_y):
        """Draw all game objects"""
        center_y = int(WINDOW_HEIGHT * 0.8)
        traffic_manager.draw(self.screen, player_world_y, center_y)
        player.draw(self.screen, int(player.x), center_y)
        feedback_hud.draw(self.screen)
    
    def finalize_frame(self):
        """Complete the frame rendering"""
        pygame.display.flip()
