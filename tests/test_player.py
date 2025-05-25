import unittest
import pygame
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from player import Player
from settings import (
    PLAYER_START_X, PLAYER_START_Y, PLAYER_HEALTH, PLAYER_SPEED, 
    PLAYER_HIT_RECT, PLAYER_IMAGE_PATH_IDLE, PLAYER_IMAGE_PATH_WALK,
    PLAYER_IMAGE_PATH_HIT, PLAYER_IMAGE_PATH_DEATH, PLAYER_IMAGE_PATH_CLIMB,
    PLAYER_IMAGE_PATH_JUMP, PLAYER_ANIMATION_SPEED,
    WORLD_WIDTH, WORLD_HEIGHT, TILESIZE, MELEE_ATTACK_DURATION,
    UI_FONT, UI_FONT_SIZE, UI_COLORS
)
from weapon import WEAPON_DATA

class TestPlayer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()
        # Minimal setup for pygame display if needed by Player sprite loading
        cls.screen = pygame.display.set_mode((1, 1), pygame.NOFRAME) 

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        """Set up a player instance for each test."""
        # Mock sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.game_state_manager = unittest.mock.Mock() # Mock game_state_manager if Player interacts with it

        self.player = Player(
            game_state_manager=self.game_state_manager,
            pos=(PLAYER_START_X, PLAYER_START_Y),
            groups=(self.all_sprites,),
            obstacle_sprites=pygame.sprite.Group(), # Mock obstacles
            item_sprites=pygame.sprite.Group(),     # Mock items
            projectiles_group=self.projectiles,
            all_sprites_group=self.all_sprites
        )

    def test_player_initialization(self):
        """Test that the player is initialized with correct default values."""
        self.assertEqual(self.player.rect.center, (PLAYER_START_X, PLAYER_START_Y))
        self.assertEqual(self.player.health, PLAYER_HEALTH)
        self.assertEqual(self.player.speed, PLAYER_SPEED)
        self.assertIsNotNone(self.player.image)
        self.assertEqual(self.player.kills, 0)
        self.assertIn(self.player.weapon.name, WEAPON_DATA.keys()) # Checks if initial weapon is valid

    def test_increment_kills(self):
        """Test that the player's kill count can be incremented."""
        initial_kills = self.player.kills
        self.player.increment_kills()
        self.assertEqual(self.player.kills, initial_kills + 1)
        self.player.increment_kills(5)
        self.assertEqual(self.player.kills, initial_kills + 1 + 5)

    def test_equip_weapon(self):
        """Test equipping a new weapon."""
        self.player.equip_weapon('shotgun') # Assuming 'shotgun' is a valid key in WEAPON_DATA
        self.assertEqual(self.player.weapon.name, 'shotgun')
        
        # Test equipping a non-existent weapon (should ideally not change or raise error)
        # For now, let's assume it defaults or keeps current if key is bad.
        # This depends on Player.equip_weapon implementation.
        current_weapon_name = self.player.weapon.name
        self.player.equip_weapon('non_existent_weapon')
        if 'non_existent_weapon' not in WEAPON_DATA:
             self.assertEqual(self.player.weapon.name, current_weapon_name)


    def test_movement_input(self):
        """Test player movement based on input (simplified)."""
        initial_pos = self.player.pos.copy()
        
        # Simulate pressing 'right'
        self.player.direction = pygame.math.Vector2(1, 0)
        self.player.update(pygame.sprite.Group(), [], 1/60) # dt = 1/60 seconds
        
        # Check if player moved right (exact position depends on speed and dt)
        self.assertGreater(self.player.pos.x, initial_pos.x)
        self.assertEqual(self.player.pos.y, initial_pos.y)

        # Simulate pressing 'down'
        initial_pos = self.player.pos.copy()
        self.player.direction = pygame.math.Vector2(0, 1)
        self.player.update(pygame.sprite.Group(), [], 1/60)
        self.assertGreater(self.player.pos.y, initial_pos.y)


    # Add more tests for other methods like shoot, melee_attack, take_damage etc.

if __name__ == '__main__':
    unittest.main()
