import pygame

class Camera:
    def __init__(self, camera_width, camera_height, world_width, world_height):
        self.camera_rect = pygame.Rect(0, 0, camera_width, camera_height)
        self.world_width = world_width
        self.world_height = world_height

    def update(self, target_sprite):
        # Updates the camera's position to follow the target_sprite (e.g., player).
        x = target_sprite.rect.centerx - self.camera_rect.width // 2
        y = target_sprite.rect.centery - self.camera_rect.height // 2

        self.camera_rect.x = max(0, min(x, self.world_width - self.camera_rect.width))
        self.camera_rect.y = max(0, min(y, self.world_height - self.camera_rect.height))

    def apply(self, target_rect):
        # Applies the camera offset to a target_rect (e.g., an entity's rect).
        # Returns a new pygame.Rect shifted by the camera's position.
        return target_rect.move(-self.camera_rect.x, -self.camera_rect.y)

    def apply_to_point(self, world_x, world_y):
        # Applies camera offset to a single point in world coordinates.
        screen_x = world_x - self.camera_rect.x
        screen_y = world_y - self.camera_rect.y
        return screen_x, screen_y

    @property
    def x(self):
        return self.camera_rect.x

    @property
    def y(self):
        return self.camera_rect.y

    @property
    def width(self):
        return self.camera_rect.width

    @property
    def height(self):
        return self.camera_rect.height
