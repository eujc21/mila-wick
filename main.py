import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CAPTION, LIGHT_GRAY,
    RADAR_RADIUS, RADAR_MARGIN, RADAR_BG_COLOR, RADAR_LINE_COLOR
)
from player import Player

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.running = True
        self.background_color = LIGHT_GRAY

        # Player setup
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        print(f"Initial Weapon: {self.player.weapon}") # Using the __str__ method of Weapon

        # Radar setup - using constants from settings.py
        self.radar_actual_radius = RADAR_RADIUS 
        self.radar_pos_x = self.radar_actual_radius + RADAR_MARGIN
        self.radar_pos_y = SCREEN_HEIGHT - self.radar_actual_radius - RADAR_MARGIN

    def draw_radar(self):
        # Create a temporary surface for the radar for alpha transparency
        radar_surface = pygame.Surface((self.radar_actual_radius * 2, self.radar_actual_radius * 2), pygame.SRCALPHA)
        # Draw the radar background circle
        pygame.draw.circle(radar_surface, RADAR_BG_COLOR, (self.radar_actual_radius, self.radar_actual_radius), self.radar_actual_radius)

        # Calculate line points for player direction
        center_x, center_y = self.radar_actual_radius, self.radar_actual_radius
        
        direction_normalized = self.player.direction.normalize() if self.player.direction.length_squared() > 0 else pygame.math.Vector2(0,1)
        
        # Line length slightly less than radius to stay inside the circle
        line_len = self.radar_actual_radius - 5 
        end_x = center_x + direction_normalized.x * line_len
        end_y = center_y + direction_normalized.y * line_len

        pygame.draw.line(radar_surface, RADAR_LINE_COLOR, (center_x, center_y), (end_x, end_y), 2)
        
        # Blit the radar surface onto the main screen
        # Adjust blit position to account for radar_surface origin (top-left of the surface)
        blit_pos_x = self.radar_pos_x - self.radar_actual_radius
        blit_pos_y = self.radar_pos_y - self.radar_actual_radius
        self.screen.blit(radar_surface, (blit_pos_x, blit_pos_y))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Update all sprites
            self.all_sprites.update()

            # Draw / render
            self.screen.fill(self.background_color)
            self.all_sprites.draw(self.screen)
            self.draw_radar()
            pygame.display.flip() 

            self.clock.tick(FPS)

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
