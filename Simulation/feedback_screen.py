import pygame
import os

class FeedbackScreen:
    def __init__(self):
        self.feedback_path = os.path.join(os.path.dirname(__file__), 'Logs', 'ai_feedback.txt')
        
    def show(self, screen, clock):
        """Display the feedback screen with scrollable text"""
        try:
            with open(self.feedback_path, 'r', encoding='utf-8') as f:
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
        max_width = min(1000, screen.get_width() - 2 * margin_x)  # Limit line length for readability

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
        max_scroll = max(0, len(lines) * line_height - screen.get_height() + margin_y)
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
                        
            screen.fill(bg_color)
            # Draw semi-transparent rectangle for text area with rounded corners effect
            text_area_width = screen.get_width() - 2 * margin_x
            text_area_height = screen.get_height() - 2 * margin_y
            s = pygame.Surface((text_area_width, text_area_height), pygame.SRCALPHA)
            s.fill(text_bg_color)
            screen.blit(s, (margin_x, margin_y))
            
            # Render text with better vertical spacing
            y = margin_y + 30 - scroll
            for line in lines:
                if line.strip() == '':
                    y += line_height // 2
                    continue
                if y > margin_y - line_height and y < screen.get_height() - margin_y:  # Only render visible lines
                    text_surface = font.render(line, True, text_color)
                    screen.blit(text_surface, (margin_x + 30, y))
                y += line_height
            
            # Draw title and instructions with better styling
            title_font = pygame.font.SysFont('segoeui', 28, bold=True)
            title_text = "AI Driving Instructor Feedback"
            title_surface = title_font.render(title_text, True, (200, 220, 255))
            title_x = (screen.get_width() - title_surface.get_width()) // 2
            screen.blit(title_surface, (title_x, 20))
            
            instr_font = pygame.font.SysFont('segoeui', 20)
            instr = "UP/DOWN arrows to scroll • ESC or Q to exit"
            instr_surface = instr_font.render(instr, True, (160, 180, 200))
            instr_x = (screen.get_width() - instr_surface.get_width()) // 2
            screen.blit(instr_surface, (instr_x, screen.get_height() - 35))
            pygame.display.flip()
            clock.tick(30)
