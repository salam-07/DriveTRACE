import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT

class EndingScreen:
    def __init__(self):
        self.selection = 0  # 0: Exit with AI Feedback, 1: Exit
        self.options = ["Exit with AI Feedback", "Exit"]
        
    def handle_input(self, event):
        """Handle input for ending screen navigation"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selection = (self.selection - 1) % 2
                return None
            elif event.key == pygame.K_DOWN:
                self.selection = (self.selection + 1) % 2
                return None
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.selection
            elif event.key == pygame.K_ESCAPE:
                return 1  # Exit
        return None
    
    def draw(self, screen):
        """Draw the ending screen"""
        # Draw dark red overlay to indicate crash/end
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((100, 0, 0, 200))  # Dark red tint
        screen.blit(overlay, (0, 0))
        
        # Screen dimensions and positioning
        screen_width = 600
        screen_height = 400
        screen_x = (WINDOW_WIDTH - screen_width) // 2
        screen_y = (WINDOW_HEIGHT - screen_height) // 2
        
        # Draw screen background
        pygame.draw.rect(screen, (60, 20, 20), (screen_x, screen_y, screen_width, screen_height))
        pygame.draw.rect(screen, (200, 100, 100), (screen_x, screen_y, screen_width, screen_height), 4)
        
        # Fixed-size fonts
        title_font = pygame.font.SysFont('arial', 48, bold=True)
        subtitle_font = pygame.font.SysFont('arial', 24)
        option_font = pygame.font.SysFont('arial', 26)
        instr_font = pygame.font.SysFont('arial', 20)
        
        # Title - CRASH/COLLISION
        title_text = "COLLISION DETECTED"
        title_surface = title_font.render(title_text, True, (255, 200, 200))
        title_x = screen_x + (screen_width - title_surface.get_width()) // 2
        screen.blit(title_surface, (title_x, screen_y + 40))
        
        # Subtitle
        subtitle_text = "Your vehicle has collided with traffic."
        subtitle_surface = subtitle_font.render(subtitle_text, True, (220, 220, 220))
        subtitle_x = screen_x + (screen_width - subtitle_surface.get_width()) // 2
        screen.blit(subtitle_surface, (subtitle_x, screen_y + 110))
        
        subtitle_text2 = "Simulation ended for safety analysis."
        subtitle_surface2 = subtitle_font.render(subtitle_text2, True, (220, 220, 220))
        subtitle_x2 = screen_x + (screen_width - subtitle_surface2.get_width()) // 2
        screen.blit(subtitle_surface2, (subtitle_x2, screen_y + 140))
        
        # Menu options
        option_y_start = screen_y + 200
        option_height = 50
        
        for i, option in enumerate(self.options):
            y_pos = option_y_start + i * option_height
            
            # Draw option background if selected
            if i == self.selection:
                pygame.draw.rect(screen, (100, 60, 60), 
                               (screen_x + 30, y_pos - 8, screen_width - 60, option_height - 10))
                pygame.draw.rect(screen, (200, 150, 150), 
                               (screen_x + 30, y_pos - 8, screen_width - 60, option_height - 10), 2)
            
            # Draw option text
            color = (255, 220, 220) if i == self.selection else (200, 200, 200)
            text_surface = option_font.render(option, True, color)
            text_x = screen_x + 50  # Left-aligned with padding
            screen.blit(text_surface, (text_x, y_pos))
        
        # Instructions at bottom
        instr_text = "UP/DOWN to navigate • ENTER/SPACE to select • ESC to exit"
        instr_surface = instr_font.render(instr_text, True, (180, 180, 180))
        instr_x = screen_x + (screen_width - instr_surface.get_width()) // 2
        screen.blit(instr_surface, (instr_x, screen_y + screen_height - 40))
