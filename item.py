'''
Defines the Item class and its derivatives, like HealthPack.
'''
import pygame
# Import settings from the correct path
from game.core.settings import ITEM_SIZE, HEALTH_PACK_COLOR, HEALTH_PACK_VALUE, BLACK # Assuming BLACK is for text or outlines

from game.core.entity import Entity # Corrected import for Entity

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type, image=None, value=None):
        super().__init__()
        self.item_type = item_type
        self.value = value

        if image:
            self.image = image
        else:
            # Default appearance if no image is provided
            self.image = pygame.Surface(ITEM_SIZE) # Corrected: Use ITEM_SIZE directly
            self.image.fill(BLACK) # Fallback color, should be customized by subclass
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def apply_effect(self, player):
        '''
        Applies the item's effect to the player.
        This method should be overridden by subclasses.
        '''
        print(f"Applying {self.item_type} effect (not implemented for base Item class).")

class HealthPack(Item):
    def __init__(self, x, y):
        super().__init__(x, y, "health_pack", value=HEALTH_PACK_VALUE)
        self.image = pygame.Surface(ITEM_SIZE) # Corrected: Use ITEM_SIZE directly
        self.image.fill(HEALTH_PACK_COLOR)
        # Optional: Add a visual cue, like a plus sign
        font = pygame.font.SysFont(None, int(ITEM_SIZE[0] * 0.8)) # Corrected: Use ITEM_SIZE[0] for font scaling
        text_surface = font.render('+', True, BLACK)
        text_rect = text_surface.get_rect(center=(ITEM_SIZE[0] / 2, ITEM_SIZE[1] / 2))
        self.image.blit(text_surface, text_rect)

    def apply_effect(self, player):
        '''
        Increases the player's health by the health pack's value.
        '''
        if player.health < player.max_health:
            player.health += self.value
            if player.health > player.max_health:
                player.health = player.max_health
            print(f"Player health restored by {self.value}. Current health: {player.health}")
        else:
            print("Player health is already full.")
