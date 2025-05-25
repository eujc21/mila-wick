import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CAPTION, LIGHT_GRAY,
    RADAR_RADIUS, RADAR_MARGIN, RADAR_BG_COLOR, RADAR_LINE_COLOR,
    WORLD_ROOM_ROWS, WORLD_ROOM_COLS, ROOM_COLORS, ROOM_WIDTH, ROOM_HEIGHT,
    MELEE_VISUAL_DURATION, MELEE_ATTACK_COLOR, BLACK # Added BLACK here
)
from player import Player
from room import Room
from projectile import Projectile # Import Projectile
from npc import NPC # Import NPC

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

        # NPC setup
        self.npcs = pygame.sprite.Group() # Group for NPCs
        npc1 = NPC(ROOM_WIDTH + 50, ROOM_HEIGHT / 2) # Example NPC in the second room (to the right)
        self.all_sprites.add(npc1)
        self.npcs.add(npc1)
        
        print(f"Initial Weapon: {self.player.weapon}")

        # Camera setup (top-left corner of the camera view in world coordinates)
        self.camera_x = 0
        self.camera_y = 0

        # Melee attack visualization
        self.melee_attack_visuals = [] # List to store (rect, creation_time, color) tuples

        # Radar setup
        self.radar_actual_radius = RADAR_RADIUS 
        self.radar_pos_x = self.radar_actual_radius + RADAR_MARGIN
        self.radar_pos_y = SCREEN_HEIGHT - self.radar_actual_radius - RADAR_MARGIN

        # Font for displaying weapon name
        self.font = pygame.font.SysFont(None, 36) # Using a default system font

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

    def draw_status_bar(self):
        """Draws the player's current weapon and health in the top-left corner."""
        weapon_name = "None"
        if self.player.weapon:
            weapon_name = self.player.weapon.name
        
        player_health = self.player.health

        weapon_text = f"Weapon: {weapon_name}"
        health_text = f"Health: {player_health}"

        weapon_surface = self.font.render(weapon_text, True, BLACK)
        health_surface = self.font.render(health_text, True, BLACK)

        self.screen.blit(weapon_surface, (10, 10))
        self.screen.blit(health_surface, (10, 10 + weapon_surface.get_height() + 5))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE: 
                        # Check weapon type before deciding action
                        if self.player.weapon.type == "ranged":
                            self.player.shoot(self.projectiles, self.all_sprites)
                        elif self.player.weapon.type == "melee":
                            attack_rect = self.player.melee_attack() # melee_attack now returns the rect
                            if attack_rect:
                                current_time = pygame.time.get_ticks()
                                self.melee_attack_visuals.append((attack_rect, current_time, MELEE_ATTACK_COLOR))
                    elif event.key == pygame.K_1: # Equip pistol
                        print("Equipping Pistol")
                        self.player.equip_weapon("pistol")
                    elif event.key == pygame.K_2: # Equip knife
                        print("Equipping Knife")
                        self.player.equip_weapon("knife")

            # Update all sprites (player and projectiles)
            # Pass player's rect to NPC update for follow logic
            for sprite in self.all_sprites:
                if isinstance(sprite, NPC):
                    sprite.update(self.player.rect)
                else:
                    sprite.update() 
            # self.projectiles.update() # No longer needed if all_sprites handles all updates
            self.update_camera() 

            self.screen.fill(LIGHT_GRAY) 

            for room in self.rooms:
                room.draw(self.screen, self.camera_x, self.camera_y)
            
            # Draw NPC patrol areas (for debugging/visualization)
            for npc_sprite in self.npcs:
                if not npc_sprite.is_following_player: # Only draw if patrolling
                    patrol_rect_world = pygame.Rect(
                        npc_sprite.patrol_limit_left, 
                        npc_sprite.rect.top, # Use NPC's current y and height for the visualization
                        npc_sprite.patrol_limit_right - npc_sprite.patrol_limit_left, 
                        npc_sprite.rect.height
                    )
                    # Convert world coordinates to screen coordinates
                    patrol_rect_screen_x = patrol_rect_world.x - self.camera_x
                    patrol_rect_screen_y = patrol_rect_world.y - self.camera_y
                    pygame.draw.rect(self.screen, (255, 255, 0, 100), 
                                     (patrol_rect_screen_x, patrol_rect_screen_y, patrol_rect_world.width, patrol_rect_world.height), 1) # Yellow, thin border

                # Draw health bar if NPC is being followed (discovered)
                if npc_sprite.is_following_player and npc_sprite.health > 0:
                    HEALTH_BAR_HEIGHT = 5
                    HEALTH_BAR_Y_OFFSET = 10 # Distance above NPC rect
                    health_percentage = npc_sprite.health / npc_sprite.max_health
                    
                    # Background of health bar (e.g., red for lost health)
                    bg_bar_width = npc_sprite.rect.width
                    bg_bar_x_world = npc_sprite.rect.x
                    bg_bar_y_world = npc_sprite.rect.top - HEALTH_BAR_Y_OFFSET
                    bg_bar_screen_x = bg_bar_x_world - self.camera_x
                    bg_bar_screen_y = bg_bar_y_world - self.camera_y
                    pygame.draw.rect(self.screen, (255, 0, 0), 
                                     (bg_bar_screen_x, bg_bar_screen_y, bg_bar_width, HEALTH_BAR_HEIGHT))

                    # Foreground of health bar (e.g., green for current health)
                    fg_bar_width = bg_bar_width * health_percentage
                    pygame.draw.rect(self.screen, (0, 255, 0), 
                                     (bg_bar_screen_x, bg_bar_screen_y, fg_bar_width, HEALTH_BAR_HEIGHT))

            # Draw all sprites (player and projectiles) relative to camera
            for sprite in self.all_sprites:
                screen_x = sprite.rect.x - self.camera_x
                screen_y = sprite.rect.y - self.camera_y
                self.screen.blit(sprite.image, (screen_x, screen_y))

            # Draw and manage melee attack visuals
            current_time = pygame.time.get_ticks()
            # Iterate over a copy for safe removal
            for visual in list(self.melee_attack_visuals):
                rect, creation_time, color = visual
                if current_time - creation_time > MELEE_VISUAL_DURATION:
                    self.melee_attack_visuals.remove(visual)
                else:
                    # Draw the melee attack rect relative to the camera
                    # We need a surface for transparency
                    temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    temp_surface.fill(color) # Fill with semi-transparent color
                    screen_rect_x = rect.x - self.camera_x
                    screen_rect_y = rect.y - self.camera_y
                    self.screen.blit(temp_surface, (screen_rect_x, screen_rect_y))
            
            self.draw_radar()
            self.draw_status_bar() # Draw the status bar
            pygame.display.flip() 
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
