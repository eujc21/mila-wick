\
import pygame
import os
# Import settings from the correct path
from game.core.settings import (
    UI_WHITE, UI_BLACK, UI_GRAY, UI_LIGHT_BLUE, 
    UI_INPUT_BOX_COLOR, UI_INPUT_TEXT_COLOR, 
    UI_PROMPT_COLOR, UI_SCORE_TEXT_COLOR, UI_CURSOR_COLOR, 
    UI_LEADERBOARD_OVERLAY_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT
)

class LeaderboardSprite:
    def __init__(self, screen, font_prompt, font_input, font_scores, leaderboard_manager, settings):
        self.screen = screen
        self.font_prompt = font_prompt
        self.font_input = font_input
        self.font_scores = font_scores
        self.leaderboard_manager = leaderboard_manager
        self.settings = settings # For SCREEN_WIDTH, SCREEN_HEIGHT, etc.

        self.is_active = False
        self.current_name_input = "" # Corrected string literal
        self.player_score_to_submit = 0
        # Modes: 'INPUT', 'SHOW_SCORES', 'SUBMITTED' (briefly to show confirmation)
        self.display_mode = 'INPUT' # Corrected string literal

        # Input box properties
        self.input_box_rect = pygame.Rect(
            self.settings.SCREEN_WIDTH // 2 - 150,
            self.settings.SCREEN_HEIGHT // 2 - 25,
            300, 50
        )
        self.max_name_length = 15

        # Cursor properties
        self.cursor_visible = True
        self.cursor_blink_interval = 500  # milliseconds
        self.last_cursor_toggle = pygame.time.get_ticks()
        
        self.prompt_message = "Enter Your Name:"
        self.score_display_message = "Your Score: {}"
        self.submit_confirm_message = "Score Submitted!"
        self.leaderboard_title = "Top Scores"
        self.restart_prompt_message = "Press R to Restart, Q to Quit"
        
        self.top_scores_cache = [] # To store fetched scores for display

    def activate(self, score):
        self.is_active = True
        self.player_score_to_submit = score
        self.current_name_input = "" # Corrected string literal
        self.display_mode = 'INPUT' # Corrected string literal
        self.last_cursor_toggle = pygame.time.get_ticks() # Reset cursor blink
        self.cursor_visible = True

    def deactivate(self):
        self.is_active = False

    def handle_event(self, event):
        if not self.is_active:
            return None

        if self.display_mode == 'INPUT': # Corrected string literal
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if self.current_name_input.strip():
                        self.leaderboard_manager.add_score(self.current_name_input.strip(), self.player_score_to_submit)
                        self.display_mode = 'SUBMITTED' # Corrected string literal
                        self.last_event_time = pygame.time.get_ticks()
                        self.top_scores_cache = self.leaderboard_manager.get_top_scores()
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    self.current_name_input = self.current_name_input[:-1]
                    return None
                elif len(self.current_name_input) < self.max_name_length:
                    if event.unicode.isalnum() or event.unicode in [' ', '_', '-']:
                        self.current_name_input += event.unicode
                    return None
        
        elif self.display_mode == 'SHOW_SCORES' or self.display_mode == 'SUBMITTED': # Corrected string literals
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return 'RESTART'
                elif event.key == pygame.K_q:
                    return 'QUIT'
        return None

    def update(self):
        if not self.is_active:
            return

        current_time = pygame.time.get_ticks()
        if self.display_mode == 'INPUT': # Corrected string literal
            if current_time - self.last_cursor_toggle > self.cursor_blink_interval:
                self.cursor_visible = not self.cursor_visible
                self.last_cursor_toggle = current_time
        elif self.display_mode == 'SUBMITTED': # Corrected string literal
            if current_time - self.last_event_time > 1500: 
                self.display_mode = 'SHOW_SCORES' # Corrected string literal

    def draw(self):
        if not self.is_active:
            return

        overlay = pygame.Surface((self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(UI_LEADERBOARD_OVERLAY_COLOR)
        self.screen.blit(overlay, (0, 0))

        if self.display_mode == 'INPUT': # Corrected string literal
            prompt_surface = self.font_prompt.render(self.prompt_message, True, UI_PROMPT_COLOR)
            prompt_rect = prompt_surface.get_rect(center=(self.settings.SCREEN_WIDTH // 2, self.input_box_rect.top - 40))
            self.screen.blit(prompt_surface, prompt_rect)

            score_text = self.score_display_message.format(self.player_score_to_submit)
            score_surface = self.font_input.render(score_text, True, UI_SCORE_TEXT_COLOR)
            score_rect = score_surface.get_rect(center=(self.settings.SCREEN_WIDTH // 2, self.input_box_rect.bottom + 80))
            self.screen.blit(score_surface, score_rect)
            
            pygame.draw.rect(self.screen, UI_INPUT_BOX_COLOR, self.input_box_rect)
            pygame.draw.rect(self.screen, UI_GRAY, self.input_box_rect, 2)

            input_text_surface = self.font_input.render(self.current_name_input, True, UI_INPUT_TEXT_COLOR)
            input_text_rect = input_text_surface.get_rect(midleft=(self.input_box_rect.left + 10, self.input_box_rect.centery))
            self.screen.blit(input_text_surface, input_text_rect)

            if self.cursor_visible:
                cursor_x = input_text_rect.right + 2
                if not self.current_name_input:
                    cursor_x = self.input_box_rect.left + 10
                cursor_y_start = self.input_box_rect.top + 5
                cursor_y_end = self.input_box_rect.bottom - 5
                pygame.draw.line(self.screen, UI_CURSOR_COLOR, (cursor_x, cursor_y_start), (cursor_x, cursor_y_end), 2)
        
        elif self.display_mode == 'SUBMITTED': # Corrected string literal
            confirm_surface = self.font_prompt.render(self.submit_confirm_message, True, UI_WHITE)
            confirm_rect = confirm_surface.get_rect(center=(self.settings.SCREEN_WIDTH // 2, self.settings.SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(confirm_surface, confirm_rect)
            
            restart_msg_surface = self.font_input.render(self.restart_prompt_message, True, UI_WHITE)
            restart_msg_rect = restart_msg_surface.get_rect(center=(self.settings.SCREEN_WIDTH // 2, self.settings.SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(restart_msg_surface, restart_msg_rect)

        elif self.display_mode == 'SHOW_SCORES': # Corrected string literal
            title_surface = self.font_prompt.render(self.leaderboard_title, True, UI_WHITE)
            title_rect = title_surface.get_rect(center=(self.settings.SCREEN_WIDTH // 2, self.settings.SCREEN_HEIGHT // 4))
            self.screen.blit(title_surface, title_rect)

            start_y = title_rect.bottom + 40
            for i, (name, score, timestamp) in enumerate(self.top_scores_cache):
                if i >= 10: 
                    break
                score_entry = f"{i+1}. {name}: {score}"
                entry_surface = self.font_scores.render(score_entry, True, UI_WHITE)
                entry_rect = entry_surface.get_rect(center=(self.settings.SCREEN_WIDTH // 2, start_y + i * 40))
                self.screen.blit(entry_surface, entry_rect)
            
            if not self.top_scores_cache:
                no_scores_surface = self.font_input.render("No scores yet!", True, UI_WHITE)
                no_scores_rect = no_scores_surface.get_rect(center=(self.settings.SCREEN_WIDTH // 2, start_y + 40))
                self.screen.blit(no_scores_surface, no_scores_rect)

            restart_msg_surface = self.font_input.render(self.restart_prompt_message, True, UI_WHITE)
            restart_msg_rect = restart_msg_surface.get_rect(center=(
                self.settings.SCREEN_WIDTH // 2, 
                self.settings.SCREEN_HEIGHT - 80
            ))
            self.screen.blit(restart_msg_surface, restart_msg_rect)
