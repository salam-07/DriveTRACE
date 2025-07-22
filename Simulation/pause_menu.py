import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT

class PauseMenu:
    def __init__(self):
        self.selection = 0  # 0: Resume, 1: Exit and Get AI Feedback, 2: Change Car, 3: Exit
        self.options = ["Resume", "Exit and Get AI Feedback", "Change Car", "Exit"]
        self.car_selection_mode = False
        self.current_car = 1  # Default car number
        self.max_cars = 17  # Based on car_1.png to car_17.png in Assets/vehicles/
        
    def handle_input(self, event):
        """Handle input for pause menu navigation"""
        if event.type == pygame.KEYDOWN:
            if self.car_selection_mode:
                # Handle car selection mode
                if event.key == pygame.K_LEFT:
                    self.current_car = ((self.current_car - 2) % self.max_cars) + 1  # Wrap around 1-17
                    return 'car_changed'
                elif event.key == pygame.K_RIGHT:
                    self.current_car = (self.current_car % self.max_cars) + 1  # Wrap around 1-17
                    return 'car_changed'
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    self.car_selection_mode = False
                    return None
            else:
                # Handle normal menu navigation
                if event.key == pygame.K_UP:
                    self.selection = (self.selection - 1) % 4
                    return None
                elif event.key == pygame.K_DOWN:
                    self.selection = (self.selection + 1) % 4
                    return None
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.selection == 2:  # Change Car option
                        self.car_selection_mode = True
                        return None
                    else:
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
        
        # Menu dimensions and positioning - made taller to accommodate new option
        menu_width = 500
        menu_height = 400
        menu_x = (WINDOW_WIDTH - menu_width) // 2
        menu_y = (WINDOW_HEIGHT - menu_height) // 2
        
        # Draw menu background
        pygame.draw.rect(screen, (40, 40, 50), (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, (120, 120, 140), (menu_x, menu_y, menu_width, menu_height), 3)
        
        # Fixed-size fonts
        title_font = pygame.font.SysFont('arial', 36, bold=True)
        option_font = pygame.font.SysFont('arial', 24)
        car_font = pygame.font.SysFont('arial', 20)
        instr_font = pygame.font.SysFont('arial', 18)
        
        # Title
        if self.car_selection_mode:
            title_text = "CHANGE CAR"
            title_color = (255, 200, 100)
        else:
            title_text = "PAUSED"
            title_color = (255, 255, 255)
        
        title_surface = title_font.render(title_text, True, title_color)
        title_x = menu_x + (menu_width - title_surface.get_width()) // 2
        screen.blit(title_surface, (title_x, menu_y + 30))
        
        if self.car_selection_mode:
            # Show car selection interface
            car_text = f"Car Choice: {self.current_car}"
            car_surface = car_font.render(car_text, True, (200, 200, 255))
            car_x = menu_x + (menu_width - car_surface.get_width()) // 2
            screen.blit(car_surface, (car_x, menu_y + 150))
            
            # Show left/right arrows
            arrow_font = pygame.font.SysFont('arial', 30, bold=True)
            left_arrow = arrow_font.render("◀", True, (150, 150, 200))
            right_arrow = arrow_font.render("▶", True, (150, 150, 200))
            screen.blit(left_arrow, (menu_x + 100, menu_y + 145))
            screen.blit(right_arrow, (menu_x + 380, menu_y + 145))
            
            # Instructions for car selection
            instr_text = "LEFT/RIGHT to change car • ENTER/SPACE/ESC to finish"
            instr_surface = instr_font.render(instr_text, True, (160, 160, 160))
            instr_x = menu_x + (menu_width - instr_surface.get_width()) // 2
            screen.blit(instr_surface, (instr_x, menu_y + menu_height - 30))
        else:
            # Menu options with fixed positioning
            option_y_start = menu_y + 100
            option_height = 45
            
            for i, option in enumerate(self.options):
                y_pos = option_y_start + i * option_height
                
                # Draw option background if selected
                if i == self.selection:
                    pygame.draw.rect(screen, (70, 70, 90), 
                                   (menu_x + 20, y_pos - 5, menu_width - 40, option_height - 10))
                
                # Draw option text
                color = (200, 200, 255) if i == self.selection else (200, 200, 200)
                
                # Special handling for Change Car option
                if option == "Change Car":
                    display_text = f"{option} (Current: {self.current_car})"
                else:
                    display_text = option
                
                text_surface = option_font.render(display_text, True, color)
                text_x = menu_x + 40  # Left-aligned with padding
                screen.blit(text_surface, (text_x, y_pos))
            
            # Instructions at bottom
            instr_text = "UP/DOWN to navigate • ENTER/SPACE to select • ESC to resume"
            instr_surface = instr_font.render(instr_text, True, (160, 160, 160))
            instr_x = menu_x + (menu_width - instr_surface.get_width()) // 2
            screen.blit(instr_surface, (instr_x, menu_y + menu_height - 30))
