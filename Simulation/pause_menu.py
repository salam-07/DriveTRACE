import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT

class PauseMenu:
    def __init__(self):
        self.selection = 0  # 0: Resume, 1: Exit and Get AI Feedback, 2: Exit
        self.options = ["Resume", "Exit and Get AI Feedback", "Exit"]
        
    def handle_input(self, event):
        """Handle input for pause menu navigation"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selection = (self.selection - 1) % 3
                return None
            elif event.key == pygame.K_DOWN:
                self.selection = (self.selection + 1) % 3
                return None
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.selection
            elif event.key == pygame.K_ESCAPE:
                return 0  # Resume
        return None
    
    def draw(self, screen):
        """Draw the pause menu"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Menu dimensions and positioning - made wider to accommodate text
        menu_width = 500
        menu_height = 350
        menu_x = (WINDOW_WIDTH - menu_width) // 2
        menu_y = (WINDOW_HEIGHT - menu_height) // 2
        
        # Draw menu background
        pygame.draw.rect(screen, (40, 40, 50), (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, (120, 120, 140), (menu_x, menu_y, menu_width, menu_height), 3)
        
        # Fixed-size fonts
        title_font = pygame.font.SysFont('arial', 36, bold=True)
        option_font = pygame.font.SysFont('arial', 24)
        instr_font = pygame.font.SysFont('arial', 18)
        
        # Title
        title_text = "PAUSED"
        title_surface = title_font.render(title_text, True, (255, 255, 255))
        title_x = menu_x + (menu_width - title_surface.get_width()) // 2
        screen.blit(title_surface, (title_x, menu_y + 40))
        
        # Menu options with fixed positioning
        option_y_start = menu_y + 120
        option_height = 45
        
        for i, option in enumerate(self.options):
            y_pos = option_y_start + i * option_height
            
            # Draw option background if selected
            if i == self.selection:
                pygame.draw.rect(screen, (70, 70, 90), 
                               (menu_x + 20, y_pos - 5, menu_width - 40, option_height - 10))
            
            # Draw option text
            color = (200, 200, 255) if i == self.selection else (200, 200, 200)
            text_surface = option_font.render(option, True, color)
            text_x = menu_x + 40  # Left-aligned with padding
            screen.blit(text_surface, (text_x, y_pos))
        
        # Instructions at bottom
        instr_text = "UP/DOWN to navigate • ENTER/SPACE to select • ESC to resume"
        instr_surface = instr_font.render(instr_text, True, (160, 160, 160))
        instr_x = menu_x + (menu_width - instr_surface.get_width()) // 2
        screen.blit(instr_surface, (instr_x, menu_y + menu_height - 30))
