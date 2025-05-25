import pygame
from settings import (
    PLAYER_RADIUS, PLAYER_SPEED, PLAYER_HEALTH, PINK, WHITE, 
    WORLD_WIDTH, WORLD_HEIGHT # Use world dimensions for clamping
)
from weapon import Weapon, WEAPON_DATA # Import Weapon class and WEAPON_DATA
from projectile import Projectile # Import Projectile
from grenade import Grenade # Import Grenade
from game.core.entity import Entity # Import Entity

class Player(Entity): # Inherit from Entity
    def __init__(self, start_x, start_y, initial_weapon_key="pistol"):
        super().__init__(x=start_x, y=start_y, health=PLAYER_HEALTH) # Call Entity's __init__
        self.radius = PLAYER_RADIUS
        self.circle_color = PINK
        self.arrow_color = WHITE
        # self.health = PLAYER_HEALTH # Removed, handled by Entity
        self.speed = PLAYER_SPEED
        self.kills = 0 # Initialize kills counter
        
        self.weapon: Weapon = None # Initialize weapon attribute
        self.equip_weapon(initial_weapon_key) # Equip initial weapon using the new method
            
        self.direction = pygame.math.Vector2(0, 1)  # Default facing direction (down)
        # self.last_shot_time = 0 # Removed, WeaponSystem handles cooldowns
        # self.last_attack_time = 0 # Removed, WeaponSystem handles cooldowns
        
        self.image = None 
        # self.rect will store player's position in WORLD coordinates
        # The image is PLAYER_RADIUS * 2 wide/high
        self.rect = pygame.Rect(0, 0, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
        self.rect.centerx = start_x # Initial position in world coordinates
        self.rect.centery = start_y # Initial position in world coordinates
        self._create_player_image() 

    # take_damage method removed, inherited from Entity

    def _create_player_image(self):
        surface_size = self.radius * 2
        new_image = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
        new_image.fill((0, 0, 0, 0))  # Transparent background

        circle_center = (self.radius, self.radius)
        pygame.draw.circle(new_image, self.circle_color, circle_center, self.radius)

        if self.direction.length_squared() > 0:
            norm_direction = self.direction.normalize()
        else:
            norm_direction = pygame.math.Vector2(0, 1) 

        arrow_length = self.radius * 0.7
        arrow_width = self.radius * 0.5
        tip = pygame.math.Vector2(circle_center) + norm_direction * arrow_length * 0.8
        perp_vec = pygame.math.Vector2(-norm_direction.y, norm_direction.x) 
        base_center_offset = norm_direction * (-arrow_length * 0.4)
        base_point1 = pygame.math.Vector2(circle_center) + base_center_offset + perp_vec * (arrow_width / 2)
        base_point2 = pygame.math.Vector2(circle_center) + base_center_offset - perp_vec * (arrow_width / 2)
        arrow_points = [(tip.x, tip.y), (base_point1.x, base_point1.y), (base_point2.x, base_point2.y)]
        pygame.draw.polygon(new_image, self.arrow_color, arrow_points)

        self.image = new_image
        # self.rect is already in world coordinates, its size is based on the image.
        # No need to re-get rect if only image content changes, unless size changes.
        # If image size could change, then: self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1

        direction_changed = False
        if dx != 0 or dy != 0:
            # Normalize the input for direction vector only
            new_direction = pygame.math.Vector2(dx, dy).normalize()
            if self.direction != new_direction: 
                self.direction = new_direction
                direction_changed = True
        
        # Create movement vector from raw dx, dy and then normalize for speed calculation
        move_vector = pygame.math.Vector2(dx, dy) 
        if move_vector.length_squared() > 0:
            move_vector = move_vector.normalize() * self.speed
        
        # Update player's world position
        self.rect.x += move_vector.x
        self.rect.y += move_vector.y

        # Keep player within the entire world boundaries
        self.rect.clamp_ip(pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))
        
        if direction_changed:
            self._create_player_image() # Redraw player image if direction changed

    # shoot method removed, handled by WeaponSystem
    # melee_attack method removed, handled by WeaponSystem
    # get_melee_attack_rect method removed, logic moved to WeaponSystem

    def increment_kills(self):
        self.kills += 1

    def equip_weapon(self, weapon_key):
        """Equips a weapon to the player based on the weapon_key."""
        if weapon_key in WEAPON_DATA:
            weapon_attrs = WEAPON_DATA[weapon_key]
            self.weapon = Weapon(**weapon_attrs)
            print(f"Player equipped {self.weapon.name}.")
            
            # current_time = pygame.time.get_ticks() # Cooldown logic moved to WeaponSystem
            # fire_rate_ms = 0
            # if hasattr(self.weapon, 'fire_rate') and isinstance(self.weapon.fire_rate, (int, float)):
            # fire_rate_ms = int(self.weapon.fire_rate * 1000)

            # self.last_shot_time = current_time # Removed
            # self.last_attack_time = current_time # Removed

            # if self.weapon.type in ["ranged", "grenade"]:
            # self.last_shot_time = current_time - (fire_rate_ms + 1) # Removed
            # if self.weapon.type == "melee":
            # self.last_attack_time = current_time - (fire_rate_ms + 1) # Removed
        else:
            print(f"Warning: Weapon key '{weapon_key}' not found in WEAPON_DATA. No weapon equipped/changed.")
            # Optionally, decide if player should keep current weapon or be unarmed
            if self.weapon is None: # If no weapon was equipped at all (e.g. on init with bad key)
                print("Player has no weapon. Defaulting to pistol.")
                self.equip_weapon("pistol") # Fallback to a default
