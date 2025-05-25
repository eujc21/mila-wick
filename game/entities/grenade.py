import pygame
from projectile import Projectile
# Updated import path for settings
from game.core.settings import ( 
    GRENADE_COLOR, GRENADE_FUSE_TIME, GRENADE_EXPLOSION_RADIUS_FACTOR, 
    GRENADE_DAMAGE, SCREEN_WIDTH, SCREEN_HEIGHT, GRENADE_EXPLOSION_COLOR,
    PROJECTILE_WIDTH, PROJECTILE_HEIGHT
)
# Import ExplosionEffect from its new location (it's used in the original explode method,
# but will be replaced by effect_manager.create_explosion)
# from game.utils.effects import ExplosionEffect # Not strictly needed if we remove the direct instantiation

class Grenade(Projectile):
    def __init__(self, x, y, direction_vector, weapon_stats, npcs_group, owner=None): # all_sprites_group removed
        # Grenade-specific stats from weapon_stats (or use defaults if not provided)
        self.fuse_time = getattr(weapon_stats, 'fuse_time', GRENADE_FUSE_TIME)
        self.explosion_radius = getattr(weapon_stats, 'explosion_radius', 
                                        (SCREEN_WIDTH + SCREEN_HEIGHT) / 2 * GRENADE_EXPLOSION_RADIUS_FACTOR)
        self.grenade_damage = getattr(weapon_stats, 'damage', GRENADE_DAMAGE) # Grenade has its own damage from weapon
        
        super().__init__(x, y, direction_vector, weapon_stats) # weapon_stats now includes grenade damage

        self.image.fill(GRENADE_COLOR) # Ensure grenade has its specific color

        self.creation_time = pygame.time.get_ticks()
        self.detonated = False
        # self.all_sprites = all_sprites_group # Removed
        self.npcs = npcs_group # To find NPCs to damage
        self.owner = owner # Store the owner (player) of the grenade

        # Grenades might not move like regular projectiles or might have a limited range/arc.
        # For simplicity, they will use projectile's speed from weapon_stats for now.
        # If they need to arc or stop, that logic would go into update().

    def update(self):
        if not self.detonated:
            super().update() # Move the grenade like a projectile

            current_time = pygame.time.get_ticks()
            # Use self.fuse_time (which is in seconds) and convert to milliseconds
            if current_time - self.creation_time > self.fuse_time * 1000: 
                # explode() now needs effect_manager, which Grenade doesn't have directly.
                # This indicates a potential design issue: Grenade.update() cannot call self.explode()
                # if explode() needs an external manager passed as an argument.
                # For now, we'll assume this will be handled by the calling context (e.g., EntityManager)
                # or Grenade will get effect_manager in its __init__.
                # The subtask for EntityManager.handle_collisions mentions it will call projectile.explode(effect_manager).
                # So, Grenade.update() should not call self.explode() directly if it can't provide effect_manager.
                # A common pattern is for update to return a status, and the manager handles the explosion.
                # For now, to match the prompt, we'll assume explode will be called externally.
                # To prevent automatic explosion from update, we might need to comment out self.explode() here,
                # or ensure it's called from a context that can provide effect_manager.
                # Let's assume the main game loop or a system will call explode with effect_manager.
                # For now, if it's called from update, it won't create a visual.
                # This is a known limitation based on the current refactoring step.
                # The subtask for EntityManager.handle_collisions will call projectile.explode(effect_manager).
                # This means the auto-explosion by fuse time in update needs to be re-thought or the
                # EntityManager needs to be responsible for checking fuse times.
                # For now, let's leave self.explode() here, but it won't create a visual.
                # This will be fixed when EntityManager calls it with the effect_manager.
                # A better solution: self.explode() should not take effect_manager.
                # Instead, it should return data for the manager to create the effect.
                # OR, the grenade stores effect_manager.
                # Given the prompt, we modify explode to take effect_manager.
                # This means Grenade.update() cannot call self.explode(effect_manager) unless effect_manager is stored.
                # This is a conflict. Let's assume the prompt implies `explode` is called by something that *has* effect_manager.
                # The `EntityManager`'s `handle_collisions` is described as calling `projectile.explode(effect_manager)`.
                # So, the `update()` method's `self.explode()` call will not work as intended without `effect_manager`.
                # I will comment out the self.explode() in update for now as per this reasoning.
                # self.explode() 
                pass # Explosion due to fuse time will be handled by a manager that can pass effect_manager
        
    def explode(self, effect_manager): # effect_manager added to signature
        if self.detonated: # Prevent multiple explosions
            return
        self.detonated = True
        print(f"Grenade exploded at ({self.rect.centerx}, {self.rect.centery}) with radius {self.explosion_radius}")
        
        # Create a visual for the explosion using EffectManager
        effect_manager.create_explosion(
            center_pos=self.rect.center,
            radius=self.explosion_radius,
            color=GRENADE_EXPLOSION_COLOR # This constant is imported
        )
        # self.all_sprites.add(explosion_visual) # Removed

        # Damage NPCs in radius
        for npc in self.npcs:
            distance_to_npc = pygame.math.Vector2(npc.rect.centerx - self.rect.centerx,
                                                  npc.rect.centery - self.rect.centery).length()
            if distance_to_npc <= self.explosion_radius:
                # Check if NPC is not already dead to prevent multiple kill counts from one explosion
                if npc.health > 0:
                    npc.take_damage(self.grenade_damage) # Apply damage
                    # Check if the NPC died from *this* grenade hit for kill count
                    if npc.health <= 0 and self.owner: 
                        # self.owner.increment_kills() # Player instance handles its own kill increment via NPC.take_damage
                        pass # Kill is now incremented in NPC.take_damage when player_instance is passed to NPC
                print(f"Grenade damaged NPC {npc} for {self.grenade_damage}")
        self.kill() # Remove grenade projectile after explosion logic

# ExplosionEffect class has been moved to game/utils/effects.py
# class ExplosionEffect(pygame.sprite.Sprite):
# ... (definition removed)
