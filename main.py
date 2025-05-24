import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CAPTION, LIGHT_GRAY,
    RADAR_RADIUS, RADAR_MARGIN, RADAR_BG_COLOR, RADAR_LINE_COLOR,
    WORLD_ROOM_ROWS, WORLD_ROOM_COLS, ROOM_COLORS, ROOM_WIDTH, ROOM_HEIGHT
)
from player import Player
from room import Room
from projectile import Projectile # Import Projectile

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.running = True

        # World and Room setup
        self.rooms = []
        for r_row in range(WORLD_ROOM_ROWS):
            for r_col in range(WORLD_ROOM_COLS):
                color_index = (r_row * WORLD_ROOM_COLS + r_col) % len(ROOM_COLORS)
                room = Room(r_col, r_row, ROOM_COLORS[color_index])
                self.rooms.append(room)

        # Player setup
        start_x = ROOM_WIDTH / 2
        start_y = ROOM_HEIGHT / 2
        self.player = Player(start_x, start_y)
        
        self.all_sprites = pygame.sprite.Group() # For player, projectiles, etc.
        self.projectiles = pygame.sprite.Group() # Specifically for projectiles (for collision, etc.)
        self.all_sprites.add(self.player) 
        
        print(f"Initial Weapon: {self.player.weapon}")

        # Camera setup (top-left corner of the camera view in world coordinates)
        self.camera_x = 0
        self.camera_y = 0

        # Radar setup
        self.radar_actual_radius = RADAR_RADIUS 
        self.radar_pos_x = self.radar_actual_radius + RADAR_MARGIN
        self.radar_pos_y = SCREEN_HEIGHT - self.radar_actual_radius - RADAR_MARGIN

    def update_camera(self):
        # Camera follows the player
        # The camera's top-left (self.camera_x, self.camera_y) should be such that
        # the player appears in the center of the screen.
        self.camera_x = self.player.rect.centerx - SCREEN_WIDTH / 2
        self.camera_y = self.player.rect.centery - SCREEN_HEIGHT / 2

        # Clamp camera to world boundaries to prevent showing empty space
        # Max camera_x is world_width - screen_width
        self.camera_x = max(0, min(self.camera_x, WORLD_ROOM_COLS * ROOM_WIDTH - SCREEN_WIDTH))
        # Max camera_y is world_height - screen_height
        self.camera_y = max(0, min(self.camera_y, WORLD_ROOM_ROWS * ROOM_HEIGHT - SCREEN_HEIGHT))

    def draw_radar(self):
        radar_surface = pygame.Surface((self.radar_actual_radius * 2, self.radar_actual_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(radar_surface, RADAR_BG_COLOR, (self.radar_actual_radius, self.radar_actual_radius), self.radar_actual_radius)
        center_x, center_y = self.radar_actual_radius, self.radar_actual_radius
        direction_normalized = self.player.direction.normalize() if self.player.direction.length_squared() > 0 else pygame.math.Vector2(0,1)
        line_len = self.radar_actual_radius - 5 
        end_x = center_x + direction_normalized.x * line_len
        end_y = center_y + direction_normalized.y * line_len
        pygame.draw.line(radar_surface, RADAR_LINE_COLOR, (center_x, center_y), (end_x, end_y), 2)
        blit_pos_x = self.radar_pos_x - self.radar_actual_radius
        blit_pos_y = self.radar_pos_y - self.radar_actual_radius
        self.screen.blit(radar_surface, (blit_pos_x, blit_pos_y))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE: 
                        # Pass both groups to shoot method
                        self.player.shoot(self.projectiles, self.all_sprites)

            # Update all sprites (player and projectiles)
            self.all_sprites.update() 
            # self.projectiles.update() # No longer needed if all_sprites handles all updates
            self.update_camera() 

            self.screen.fill(LIGHT_GRAY) 

            for room in self.rooms:
                room.draw(self.screen, self.camera_x, self.camera_y)
            
            # Draw all sprites (player and projectiles) relative to camera
            for sprite in self.all_sprites:
                screen_x = sprite.rect.x - self.camera_x
                screen_y = sprite.rect.y - self.camera_y
                self.screen.blit(sprite.image, (screen_x, screen_y))
            
            self.draw_radar()
            pygame.display.flip() 
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
