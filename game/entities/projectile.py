import pygame
# Import settings from the correct path
from game.core.settings import PROJECTILE_WIDTH, PROJECTILE_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT, PROJECTILE_MAX_RANGE, DEFAULT_PROJECTILE_COLOR

from game.core.entity import Entity # Corrected import for Entity

class Projectile(Entity): # Inherit from Entity
    def __init__(self, x, y, direction_vector, weapon_stats): # weapon_stats is a Weapon object
        super().__init__(x=x, y=y, health=1) # Call Entity's __init__ with nominal health
        # Directly access attributes from the Weapon object
        self.color = weapon_stats.projectile_color 
        self.speed = weapon_stats.projectile_speed
        self.damage = weapon_stats.damage

        self.image = pygame.Surface([PROJECTILE_WIDTH, PROJECTILE_HEIGHT])
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        # Store original position for range calculation
        self.start_x = x
        self.start_y = y

        # Ensure direction_vector is normalized
        if direction_vector.length_squared() > 0:
            self.direction = direction_vector.normalize()
        else:
            self.direction = pygame.math.Vector2(0, -1) # Default to up if direction is zero

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # Calculate distance traveled
        distance_traveled = pygame.math.Vector2(self.rect.centerx - self.start_x, self.rect.centery - self.start_y).length()

        # Remove projectile if it goes off the world boundaries or exceeds max range
        if not pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT).colliderect(self.rect) or \
           distance_traveled > PROJECTILE_MAX_RANGE:
            self.kill() # Remove from all sprite groups

if __name__ == '__main__':
    # Example usage (requires Pygame screen and a dummy weapon_stats)
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Projectile Test")

    # Dummy weapon stats for testing
    test_weapon_stats = type('Weapon', (object,), {
        "projectile_color": (0, 255, 0), # Green
        "projectile_speed": 10,
        "damage": 10
    })()
    
    # Create a projectile instance
    # Shoots from center, upwards
    proj = Projectile(screen_width // 2, screen_height // 2, pygame.math.Vector2(0, -1), test_weapon_stats)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(proj)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        all_sprites.update()
        
        screen.fill((30,30,30)) # Dark background
        all_sprites.draw(screen) # Draw projectiles
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
