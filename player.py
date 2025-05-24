\
import pygame
from settings import (
    PLAYER_RADIUS, PLAYER_SPEED, PLAYER_HEALTH, PINK, WHITE, 
    SCREEN_WIDTH, SCREEN_HEIGHT
)
from weapon import generate_weapon, Weapon

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
        
        self.image = None 
        self.rect = None
        self._create_player_image() 
        self.rect.centerx = start_x
        self.rect.centery = start_y

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
        if self.rect:
            current_center = self.rect.center
            self.rect = self.image.get_rect(center=current_center)
        else:
            self.rect = self.image.get_rect()

    def update(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1

        direction_changed = False
        if dx != 0 or dy != 0:
            new_direction = pygame.math.Vector2(dx, dy)
            if self.direction != new_direction: # Compare vectors directly
                self.direction = new_direction
                direction_changed = True
        
        move_vector = pygame.math.Vector2(dx, dy)
        if move_vector.length_squared() > 0:
            move_vector = move_vector.normalize() * self.speed
        
        self.rect.x += move_vector.x
        self.rect.y += move_vector.y

        # Keep player on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        if direction_changed:
            self._create_player_image()
