import unittest
import pygame
import os
import sys
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from leaderboard_sprite import LeaderboardSprite
from leaderboard import Leaderboard # For mocking
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, UI_COLORS, UI_FONT, UI_FONT_SIZE

class TestLeaderboardSprite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()
        # Pygame font needs to be initialized
        pygame.font.init()
        # Minimal display setup, LeaderboardSprite might try to draw on it
        cls.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    @classmethod
    def tearDownClass(cls):
        pygame.font.quit()
        pygame.quit()

    def setUp(self):
        """Set up a LeaderboardSprite instance for each test."""
        self.mock_leaderboard_manager = MagicMock(spec=Leaderboard)
        self.mock_leaderboard_manager.get_top_scores.return_value = [
            MagicMock(name='Player1', score=100),
            MagicMock(name='Player2', score=90)
        ]
        
        # Mock fonts
        self.mock_title_font = MagicMock(spec=pygame.font.Font)
        self.mock_title_font.render.return_value = MagicMock(spec=pygame.Surface, get_rect=MagicMock(return_value=pygame.Rect(0,0,100,20)))
        
        self.mock_score_font = MagicMock(spec=pygame.font.Font)
        self.mock_score_font.render.return_value = MagicMock(spec=pygame.Surface, get_rect=MagicMock(return_value=pygame.Rect(0,0,80,15)))
        
        self.mock_input_font = MagicMock(spec=pygame.font.Font)
        self.mock_input_font.render.return_value = MagicMock(spec=pygame.Surface, get_rect=MagicMock(return_value=pygame.Rect(0,0,120,25)))

        self.fonts = {
            'title': self.mock_title_font,
            'score': self.mock_score_font,
            'input': self.mock_input_font
        }
        
        # Mock settings module if LeaderboardSprite imports it directly
        # For now, assume colors are passed or accessible via a settings object
        self.mock_settings = MagicMock()
        self.mock_settings.UI_COLORS = UI_COLORS
        self.mock_settings.UI_BG_COLOR = UI_COLORS['background']
        self.mock_settings.UI_TEXT_COLOR = UI_COLORS['text']
        self.mock_settings.UI_HIGHLIGHT_COLOR = UI_COLORS['highlight']
        self.mock_settings.UI_INPUT_BG_COLOR = UI_COLORS['input_background']
        self.mock_settings.UI_INPUT_TEXT_COLOR = UI_COLORS['input_text']
        self.mock_settings.UI_BORDER_COLOR = UI_COLORS['border']


        self.leaderboard_sprite = LeaderboardSprite(
            screen=self.screen,
            fonts=self.fonts,
            leaderboard_manager=self.mock_leaderboard_manager,
            settings=self.mock_settings # Pass the mock settings
        )

    def test_initialization(self):
        """Test that LeaderboardSprite initializes correctly."""
        self.assertFalse(self.leaderboard_sprite.active)
        self.assertEqual(self.leaderboard_sprite.player_name, "")
        self.assertIsNone(self.leaderboard_sprite.current_score)
        self.assertIsNotNone(self.leaderboard_sprite.input_rect)

    def test_activate(self):
        """Test activating the leaderboard display."""
        self.leaderboard_sprite.activate(player_score=150)
        self.assertTrue(self.leaderboard_sprite.active)
        self.assertEqual(self.leaderboard_sprite.current_score, 150)
        self.mock_leaderboard_manager.get_top_scores.assert_called_once()

    def test_deactivate(self):
        """Test deactivating the leaderboard display."""
        self.leaderboard_sprite.activate(player_score=100) # Activate first
        self.leaderboard_sprite.deactivate()
        self.assertFalse(self.leaderboard_sprite.active)
        self.assertEqual(self.leaderboard_sprite.player_name, "") # Name should be reset
        self.assertIsNone(self.leaderboard_sprite.current_score)

    def test_handle_event_typing(self):
        """Test handling text input events."""
        self.leaderboard_sprite.activate(100)
        
        # Simulate typing 'A'
        event_a = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, unicode='a')
        self.leaderboard_sprite.handle_event(event_a)
        self.assertEqual(self.leaderboard_sprite.player_name, "a")

        # Simulate typing 'B'
        event_b = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_b, unicode='B')
        self.leaderboard_sprite.handle_event(event_b)
        self.assertEqual(self.leaderboard_sprite.player_name, "aB")

    def test_handle_event_backspace(self):
        """Test handling backspace event."""
        self.leaderboard_sprite.activate(100)
        self.leaderboard_sprite.player_name = "Test"
        
        event_backspace = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE)
        self.leaderboard_sprite.handle_event(event_backspace)
        self.assertEqual(self.leaderboard_sprite.player_name, "Tes")

    def test_handle_event_enter_save_score(self):
        """Test handling enter key to save score."""
        self.leaderboard_sprite.activate(player_score=200)
        self.leaderboard_sprite.player_name = "Winner"
        
        event_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        action = self.leaderboard_sprite.handle_event(event_enter)
        
        self.mock_leaderboard_manager.add_score.assert_called_once_with("Winner", 200)
        self.assertEqual(action, "RESTART") # Or whatever action is returned after saving
        self.assertFalse(self.leaderboard_sprite.active) # Should deactivate after saving

    def test_handle_event_enter_empty_name(self):
        """Test handling enter key with an empty name (should not save)."""
        self.leaderboard_sprite.activate(player_score=50)
        self.leaderboard_sprite.player_name = ""
        
        event_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        action = self.leaderboard_sprite.handle_event(event_enter)
        
        self.mock_leaderboard_manager.add_score.assert_not_called()
        self.assertIsNone(action) # Or specific behavior for empty name submission
        self.assertTrue(self.leaderboard_sprite.active) # Should remain active

    def test_draw_calls_render(self):
        """Test that the draw method calls font render methods when active."""
        self.leaderboard_sprite.activate(100)
        self.leaderboard_sprite.draw()
        
        self.fonts['title'].render.assert_called()
        self.fonts['score'].render.assert_called() # Will be called for each score + header
        self.fonts['input'].render.assert_called()

    # More tests can be added for button interactions if they exist (e.g., Restart, Quit buttons)
    # and for how the scores are displayed.

if __name__ == '__main__':
    unittest.main()

