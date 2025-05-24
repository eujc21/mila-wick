\
import pygame
from settings import (
    PLAYER_RADIUS, PLAYER_SPEED, PLAYER_HEALTH, PINK, WHITE, 
    WORLD_WIDTH, WORLD_HEIGHT # Use world dimensions for clamping
)
from weapon import generate_weapon, Weapon
from projectile import Projectile # Import Projectile

class Player(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y):
        super().__init__()
        self.radius = PLAYER_RADIUS
        self.circle_color = PINK
        self.arrow_color = WHITE
        self.health = PLAYER_HEALTH
        self.speed = PLAYER_SPEED
        self.weapon: Weapon = generate_weapon()
        self.direction = pygame.math.Vector2(0, 1)  # Default facing direction (down)
        self.last_shot_time = 0 # Player tracks their own shot cooldown
        
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

    def shoot(self, projectiles_group, all_sprites_group):
        """Creates a projectile if the fire rate cooldown has passed."""
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
            
            projectile = Projectile(proj_x, proj_y, fire_direction, self.weapon)
            projectiles_group.add(projectile)
            all_sprites_group.add(projectile) # Add to the main drawing/update group
