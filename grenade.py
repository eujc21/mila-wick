import pygame
from projectile import Projectile
from settings import (
    GRENADE_COLOR, GRENADE_FUSE_TIME, GRENADE_EXPLOSION_RADIUS_FACTOR, 
    GRENADE_DAMAGE, SCREEN_WIDTH, SCREEN_HEIGHT, GRENADE_EXPLOSION_COLOR,
    PROJECTILE_WIDTH, PROJECTILE_HEIGHT # Assuming grenades can use default projectile size for now
)

class Grenade(Projectile):
    def __init__(self, x, y, direction_vector, weapon_stats, all_sprites_group, npcs_group, owner=None):
        # Grenade-specific stats from weapon_stats (or use defaults if not provided)
        self.fuse_time = getattr(weapon_stats, 'fuse_time', GRENADE_FUSE_TIME)
        self.explosion_radius = getattr(weapon_stats, 'explosion_radius', 
                                        (SCREEN_WIDTH + SCREEN_HEIGHT) / 2 * GRENADE_EXPLOSION_RADIUS_FACTOR)
        self.grenade_damage = getattr(weapon_stats, 'damage', GRENADE_DAMAGE) # Grenade has its own damage from weapon
        
        # Override projectile_color and damage for the super().__init__() call if they are specific to grenade
        # For now, we assume weapon_stats passed to Projectile's init will handle this.
        # If a grenade weapon always has GRENADE_COLOR, we could force it here.
        # weapon_stats.projectile_color = GRENADE_COLOR # Example if grenade color is fixed
        
        super().__init__(x, y, direction_vector, weapon_stats) # weapon_stats now includes grenade damage

        self.image.fill(GRENADE_COLOR) # Ensure grenade has its specific color

        self.creation_time = pygame.time.get_ticks()
        self.detonated = False
        self.all_sprites = all_sprites_group # To add explosion visual effect
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
                self.explode()
                # self.detonated = True # explode() now sets this
                # self.kill() # explode() now kills the grenade
        
    def explode(self):
        if self.detonated: # Prevent multiple explosions
            return
        self.detonated = True
        print(f"Grenade exploded at ({self.rect.centerx}, {self.rect.centery}) with radius {self.explosion_radius}")
        
        # Create a visual for the explosion
        explosion_visual = ExplosionEffect(self.rect.center, self.explosion_radius, GRENADE_EXPLOSION_COLOR)
        self.all_sprites.add(explosion_visual)

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

class ExplosionEffect(pygame.sprite.Sprite):
    def __init__(self, center, radius, color, duration=200): # Duration in ms
        super().__init__()
        self.radius = radius
        self.color = color
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=center)
        self.creation_time = pygame.time.get_ticks()
        self.duration = duration

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.creation_time > self.duration:
            self.kill()
