import pygame
from settings import MELEE_ATTACK_COLOR, MELEE_VISUAL_DURATION

class AttackVisual(pygame.sprite.Sprite):
    def __init__(self, center_pos, width, height, direction_vector, color=MELEE_ATTACK_COLOR, duration=MELEE_VISUAL_DURATION):
        super().__init__()
        self.color = color
        self.duration = duration
        self.creation_time = pygame.time.get_ticks()

        # Create a surface for the visual. Using SRCALPHA for potential transparency.
        # The image will be rotated, so start with a base image.
        # For simplicity, let's make the base image horizontal (width along x-axis).
        # The actual width of the visual will be its "length" (like a sword swipe).
        # The actual height will be its "thickness".
        
        # Let's assume width is the "length" of the attack (e.g., weapon range)
        # and height is the "thickness" of the attack visual.
        # Ensure width and height are positive for Surface creation
        vis_width = max(1, int(width))
        vis_height = max(1, int(height))
        self.original_image = pygame.Surface([vis_width, vis_height], pygame.SRCALPHA)
        self.original_image.fill(self.color)
        
        self.image = self.original_image
        self.rect = self.image.get_rect(center=center_pos)

        # Rotate the image based on the direction_vector
        if direction_vector.length_squared() > 0:
            # angle_to(Vector2(1,0)) gives angle with positive x-axis, negate for pygame rotation (clockwise)
            angle = -direction_vector.angle_to(pygame.math.Vector2(1, 0)) 
            self.image = pygame.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect(center=center_pos) # Update rect after rotation

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.creation_time > self.duration:
            self.kill() # Remove the sprite after its duration
