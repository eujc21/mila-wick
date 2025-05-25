\
import pygame
from settings import (
    PLAYER_RADIUS, PLAYER_SPEED, PLAYER_HEALTH, PINK, WHITE, 
    WORLD_WIDTH, WORLD_HEIGHT # Use world dimensions for clamping
)
from weapon import Weapon, WEAPON_DATA # Import Weapon class and WEAPON_DATA
from projectile import Projectile # Import Projectile
from grenade import Grenade # Import Grenade

class Player(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, initial_weapon_key="pistol"):
        super().__init__()
        self.radius = PLAYER_RADIUS
        self.circle_color = PINK
        self.arrow_color = WHITE
        self.health = PLAYER_HEALTH
        self.speed = PLAYER_SPEED
        self.kills = 0 # Initialize kills counter
        
        self.weapon: Weapon = None # Initialize weapon attribute
        self.equip_weapon(initial_weapon_key) # Equip initial weapon using the new method
            
        self.direction = pygame.math.Vector2(0, 1)  # Default facing direction (down)
        self.last_shot_time = 0 # Player tracks their own shot cooldown
        self.last_attack_time = 0 # For melee attacks
        
        self.image = None 
        # self.rect will store player's position in WORLD coordinates
        # The image is PLAYER_RADIUS * 2 wide/high
        self.rect = pygame.Rect(0, 0, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
        self.rect.centerx = start_x # Initial position in world coordinates
        self.rect.centery = start_y # Initial position in world coordinates
        self._create_player_image() 

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

    def shoot(self, projectiles_group, all_sprites_group, npcs_group=None): # Added npcs_group
        """Creates a projectile or grenade if the fire rate cooldown has passed and weapon is ranged or grenade."""
        if self.weapon.type not in ["ranged", "grenade"]:
            print(f"Cannot shoot with {self.weapon.name}, it's a {self.weapon.type} weapon.")
            return

        current_time = pygame.time.get_ticks()
        # Fire rate is in seconds, convert to milliseconds for comparison
        if current_time - self.last_shot_time > self.weapon.fire_rate * 1000:
            self.last_shot_time = current_time
            
            # Spawn projectile slightly in front of the player based on direction
            # Ensure direction is normalized before using for offset calculation
            fire_direction = self.direction.normalize() if self.direction.length_squared() > 0 else pygame.math.Vector2(0,1)
            spawn_offset_distance = self.radius + 5 # 5 pixels in front of the radius edge
            spawn_offset = fire_direction * spawn_offset_distance
            
            proj_x = self.rect.centerx + spawn_offset.x
            proj_y = self.rect.centery + spawn_offset.y
            
            if self.weapon.type == "grenade":
                if npcs_group is None:
                    print("Error: npcs_group not provided for grenade launch.")
                    return # Or handle error appropriately
                
                grenade = Grenade(
                    proj_x, proj_y, fire_direction, self.weapon,
                    all_sprites_group, npcs_group, # Pass these groups
                    self # Pass the player instance as the owner
                )
                projectiles_group.add(grenade) # Grenades are also projectiles
                all_sprites_group.add(grenade)
            elif self.weapon.type == "ranged":
                projectile = Projectile(proj_x, proj_y, fire_direction, self.weapon)
                projectiles_group.add(projectile)
                all_sprites_group.add(projectile) # Add to the main drawing/update group

    def melee_attack(self):
        """Performs a melee attack if the cooldown has passed and weapon is melee."""
        if self.weapon.type != "melee":
            # Optionally, could print a message or handle trying to melee with a ranged weapon
            # print(f"Cannot perform melee attack with {self.weapon.name}, it's a ranged weapon.")
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.weapon.fire_rate * 1000: # Using fire_rate as attack speed
            self.last_attack_time = current_time
            
            print(f"Player performed a melee attack with {self.weapon.name}!")
            attack_rect = self.get_melee_attack_rect()
            if attack_rect:
                # For debugging or visual feedback later, we know the area
                print(f"Melee attack rect: {attack_rect} (Range: {getattr(self.weapon, 'range', 'N/A')})")
            
            # Future implementation:
            # for enemy in enemies_group: # Assuming an enemies_group exists
            #     if attack_rect and attack_rect.colliderect(enemy.rect):
            #         enemy.take_damage(self.weapon.damage)
            #         print(f"Hit {enemy} with {self.weapon.name} for {self.weapon.damage} damage!")
            return attack_rect # Return the attack rect for visualization
        return None # No attack performed or no rect generated

    def increment_kills(self):
        self.kills += 1

    def equip_weapon(self, weapon_key):
        """Equips a weapon to the player based on the weapon_key."""
        if weapon_key in WEAPON_DATA:
            weapon_attrs = WEAPON_DATA[weapon_key]
            self.weapon = Weapon(**weapon_attrs)
            print(f"Player equipped {self.weapon.name}.")
            
            current_time = pygame.time.get_ticks()
            
            fire_rate_ms = 0
            # Ensure fire_rate exists and is a number before using it
            if hasattr(self.weapon, 'fire_rate') and isinstance(self.weapon.fire_rate, (int, float)):
                fire_rate_ms = int(self.weapon.fire_rate * 1000)

            # Default to starting the cooldown (old behavior if not overridden below)
            self.last_shot_time = current_time
            self.last_attack_time = current_time

            # Make the first shot/attack available immediately after equipping
            if self.weapon.type in ["ranged", "grenade"]:
                # Set last_shot_time so that (current_time - self.last_shot_time) > fire_rate_ms
                self.last_shot_time = current_time - (fire_rate_ms + 1)
            
            if self.weapon.type == "melee":
                # Set last_attack_time so that (current_time - self.last_attack_time) > fire_rate_ms
                self.last_attack_time = current_time - (fire_rate_ms + 1)
        else:
            print(f"Warning: Weapon key '{weapon_key}' not found in WEAPON_DATA. No weapon equipped/changed.")
            # Optionally, decide if player should keep current weapon or be unarmed
            if self.weapon is None: # If no weapon was equipped at all (e.g. on init with bad key)
                print("Player has no weapon. Defaulting to pistol.")
                self.equip_weapon("pistol") # Fallback to a default

    def get_melee_attack_rect(self):
        """Defines the melee attack area in front of the player."""
        if not hasattr(self.weapon, 'range') or self.weapon.type != "melee":
            return None

        attack_range = self.weapon.range
        
        # Normalized direction vector for the attack
        norm_direction = self.direction.normalize() if self.direction.length_squared() > 0 else pygame.math.Vector2(0,1)

        # Calculate the center of the attack rectangle.
        # It's positioned extending from the player's edge up to attack_range.
        # So, its center is player.center + direction * (player_radius + half_range).
        # Let's define it as a rect in front of the player.
        # The center of this rectangle would be offset from player center by player_radius + half_range.
        
        # Simpler: Position the attack area to start slightly in front of the player and extend by range.
        # Offset the start of the rect from player center by player radius along direction.
        rect_start_offset = norm_direction * self.radius
        
        # The attack rect's effective center will be along the direction, half the range from this start point.
        effective_center_x = self.rect.centerx + norm_direction.x * (self.radius + attack_range / 2.0)
        effective_center_y = self.rect.centery + norm_direction.y * (self.radius + attack_range / 2.0)

        rect_width = 0
        rect_height = 0

        # Determine dimensions based on attack direction
        # If attack is primarily horizontal, rect is long (range) and has a certain width (e.g., player radius * 1.5)
        # If attack is primarily vertical, rect is tall (range) and has a certain width.
        perpendicular_width = self.radius * 1.5 # Width of the swipe/stab

        if abs(norm_direction.x) > abs(norm_direction.y): # More horizontal attack
            rect_width = attack_range
            rect_height = perpendicular_width
        else: # More vertical attack (or perfectly diagonal)
            rect_width = perpendicular_width
            rect_height = attack_range
            
        # Create the rectangle at its calculated center
        final_attack_rect = pygame.Rect(0, 0, rect_width, rect_height)
        final_attack_rect.center = (effective_center_x, effective_center_y)
        
        return final_attack_rect
