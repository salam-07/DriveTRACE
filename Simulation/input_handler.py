import pygame
from ai_feedback import generate_and_save_feedback

class InputHandler:
    def __init__(self):
        self.paused = False
        
    def handle_events(self, pause_menu, feedback_screen, clock, screen, sound_manager, player, game):
        """Handle all pygame events and return game state"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.paused:
                    # Handle pause menu navigation
                    result = pause_menu.handle_input(event)
                    if result is not None:
                        if result == 0:  # Resume
                            self.paused = False
                            sound_manager.resume_all_sounds()
                        elif result == 1:  # Exit and Get AI Feedback
                            generate_and_save_feedback()
                            feedback_screen.show(screen, clock)
                            return False
                        elif result == 4:  # Exit (moved to position 4)
                            return False
                        elif result == 'car_changed':
                            # Update player car sprite
                            player.change_car(pause_menu.current_car)
                        elif result == 'road_changed':
                            # Update game road texture
                            game.change_road(pause_menu.current_road)
                else:
                    # Handle normal game input
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        return False
                    elif event.key == pygame.K_SPACE:
                        self.paused = True
                        sound_manager.pause_all_sounds()
                        pause_menu.selection = 0  # Default to Resume
                    elif event.key == pygame.K_e:
                        # Generate feedback before showing feedback screen
                        generate_and_save_feedback()
                        feedback_screen.show(screen, clock)
                        return False
                    elif event.key == pygame.K_t:
                        return 'toggle_traffic'
        return True
    
    def get_continuous_input(self):
        """Get continuous key presses for player movement"""
        if not self.paused:
            return pygame.key.get_pressed()
        return None
