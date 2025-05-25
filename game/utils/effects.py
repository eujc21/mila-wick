import pygame
# Ensure all necessary settings are imported for the classes below
from game.core.settings import MELEE_ATTACK_COLOR, MELEE_VISUAL_DURATION, GRENADE_EXPLOSION_COLOR
# Add any other specific settings constants if AttackVisual or ExplosionEffect use them directly.

class AttackVisual(pygame.sprite.Sprite):
    def __init__(self, center_pos, width, height, direction_vector, color=None, duration=None):
        super().__init__()
        # Use provided color or default from settings
        self.color = color if color is not None else MELEE_ATTACK_COLOR
        # Use provided duration or default from settings
        self.duration = duration if duration is not None else MELEE_VISUAL_DURATION
        self.creation_time = pygame.time.get_ticks()

        vis_width = max(1, int(width))
        vis_height = max(1, int(height))
        self.original_image = pygame.Surface([vis_width, vis_height], pygame.SRCALPHA)
        self.original_image.fill(self.color)
        
        self.image = self.original_image
        self.rect = self.image.get_rect(center=center_pos)

        if direction_vector.length_squared() > 0:
            angle = -direction_vector.angle_to(pygame.math.Vector2(1, 0)) 
            self.image = pygame.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect(center=center_pos)

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.creation_time > self.duration:
            self.kill()

class ExplosionEffect(pygame.sprite.Sprite):
    def __init__(self, center, radius, color, duration=200): # Duration in ms
        super().__init__()
        self.radius = radius
        self.color = color # Expect GRENADE_EXPLOSION_COLOR to be passed if that's the default
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=center)
        self.creation_time = pygame.time.get_ticks()
        self.duration = duration

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.creation_time > self.duration:
            self.kill()

class EffectManager:
    def __init__(self):
        self.effects = pygame.sprite.Group() # This group will be managed by EffectManager

    def create_attack_visual(self, center_pos, width, height, direction_vector, color=None, duration=None):
        # Uses MELEE_ATTACK_COLOR, MELEE_VISUAL_DURATION from settings if not provided
        # These should be imported at the top of effects.py:
        # from game.core.settings import MELEE_ATTACK_COLOR, MELEE_VISUAL_DURATION
        
        # Defaulting logic:
        # final_color = color if color is not None else MELEE_ATTACK_COLOR
        # final_duration = duration if duration is not None else MELEE_VISUAL_DURATION
        # The AttackVisual class itself handles these defaults if its params are None,
        # but its defaults are MELEE_ATTACK_COLOR and MELEE_VISUAL_DURATION directly.
        # So, EffectManager can just pass them through.

        effect = AttackVisual(
            center_pos=center_pos,
            width=width,
            height=height,
            direction_vector=direction_vector,
            color=color, # Pass None to use AttackVisual's default
            duration=duration # Pass None to use AttackVisual's default
        )
        self.effects.add(effect)
        # Note: The original plan was to add to self.effects AND self.all_sprites.
        # For better encapsulation, EffectManager should manage its own group.
        # The Game loop will then need to update and draw self.effect_manager.effects.

    def create_explosion(self, center_pos, radius, color=None, duration=None):
        # Uses GRENADE_EXPLOSION_COLOR from settings if not provided.
        # from game.core.settings import GRENADE_EXPLOSION_COLOR
        # final_color = color if color is not None else GRENADE_EXPLOSION_COLOR
        # ExplosionEffect constructor takes color and duration directly.
        # Its default duration is 200ms. Color is required.
        
        # Defaulting logic for color:
        # final_color = color if color is not None else GRENADE_EXPLOSION_COLOR
        # For duration, ExplosionEffect has its own default.
        # Let's ensure color is always passed.
        
        # We need GRENADE_EXPLOSION_COLOR from game.core.settings for the default.
        # This will be resolved when imports are added to the top of the file.

        final_color = color if color is not None else GRENADE_EXPLOSION_COLOR

        effect = ExplosionEffect(
            center=center_pos,
            radius=radius,
            color=final_color, # ExplosionEffect requires color
            duration=duration if duration is not None else 200 # Pass explicit duration or ExplosionEffect's default
        )
        self.effects.add(effect)

    def update(self, dt=None): # dt might be needed if effects have dt-sensitive updates
        self.effects.update() # Pygame groups call update on their sprites (AttackVisual, ExplosionEffect already have update())

    def draw(self, surface, camera): # Effects need to be drawn relative to camera
        for effect in self.effects:
            if hasattr(effect, 'rect') and hasattr(effect, 'image'):
                surface.blit(effect.image, camera.apply(effect.rect))
        # Alternatively, if camera.apply can be done inside effect.draw(surface, camera):
        # self.effects.draw(surface, camera) # This would require custom draw in each effect
