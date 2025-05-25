import pygame
from game.core.settings import ( # Adjusted import
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CAPTION, LIGHT_GRAY,
    RADAR_RADIUS, RADAR_MARGIN, RADAR_BG_COLOR, RADAR_LINE_COLOR,
    WORLD_ROOM_ROWS, WORLD_ROOM_COLS, ROOM_COLORS, ROOM_WIDTH, ROOM_HEIGHT,
    WORLD_WIDTH, WORLD_HEIGHT,
    MELEE_VISUAL_DURATION, MELEE_ATTACK_COLOR, BLACK,
    MINIMAP_WIDTH, MINIMAP_HEIGHT, MINIMAP_MARGIN, MINIMAP_BG_COLOR,
    MINIMAP_ROOM_COLOR, MINIMAP_PLAYER_COLOR, MINIMAP_BORDER_COLOR
)
import game.core.settings as settings_module # Adjusted import for LeaderboardSprite
from game.entities.player import Player # Adjusted import
from game.world.room import Room # Adjusted import
from game.entities.projectile import Projectile # Adjusted import
from game.entities.npc import NPC # Adjusted import
from game.entities.grenade import Grenade # Adjusted import
from game.systems.wave_manager import WaveManager # Already correct
from game.ui.leaderboard import Leaderboard # Adjusted import
from game.ui.leaderboard_sprite import LeaderboardSprite # Adjusted import
from game.systems.entity_manager import EntityManager # Added import
from game.systems.combat_system import CombatManager # Added import
from game.ui.ui_manager import UIManager # Added import
from game.core.camera import Camera # Added import

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False # Added game_over state

        # World and Room setup
        self.rooms = []
        for r_row in range(WORLD_ROOM_ROWS):
            for r_col in range(WORLD_ROOM_COLS):
                color_index = (r_row * WORLD_ROOM_COLS + r_col) % len(ROOM_COLORS)
                room = Room(r_col, r_row, ROOM_COLORS[color_index])
                self.rooms.append(room)

        # Manager Instantiation
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT)
        self.entity_manager = EntityManager()
        self.combat_manager = CombatManager(self.entity_manager)
        # Note: settings_module is already imported as 'import game.core.settings as settings_module'
        self.ui_manager = UIManager(self.screen, settings_module) 
        # self.all_sprites, self.projectiles, self.npcs pygame.sprite.Group() initializations are removed.
        # Game class will now use self.entity_manager.entities, .projectiles, .npcs

        # Player setup
        start_x = ROOM_WIDTH / 2
        start_y = ROOM_HEIGHT / 2
        self.player = Player(start_x, start_y)
        self.entity_manager.add_entity(self.player, "player") # Add player via entity_manager
        # self.all_sprites.add(self.player) # Removed

        # WaveManager setup
        self.wave_manager = WaveManager(
            all_sprites_group=self.entity_manager.entities, # Use EntityManager's group
            npcs_group=self.entity_manager.npcs,           # Use EntityManager's group
            player_reference=self.player
        )
        
        print(f"Initial Weapon: {self.player.weapon}")

        # Old self.camera_x and self.camera_y direct attributes are removed.
        # Access via self.camera.x and self.camera.y (properties of Camera class)

        # Melee attack visualization
        self.melee_attack_visuals = [] # List to store (rect, creation_time, color) tuples

        # Radar setup
        self.radar_actual_radius = RADAR_RADIUS 
        self.radar_pos_x = self.radar_actual_radius + RADAR_MARGIN
        self.radar_pos_y = SCREEN_HEIGHT - self.radar_actual_radius - RADAR_MARGIN

        # Font for displaying weapon name
        self.font = pygame.font.SysFont(None, 36) # Using a default system font
        self.game_over_font = pygame.font.SysFont(None, 72) # Font for Game Over message
        self.restart_font = pygame.font.SysFont(None, 48) # Font for Restart prompt

        # Fonts for LeaderboardSprite
        self.leaderboard_font_prompt = pygame.font.SysFont(None, 48)
        self.leaderboard_font_input = pygame.font.SysFont(None, 40)
        self.leaderboard_font_scores = pygame.font.SysFont(None, 36)

        # Leaderboard setup
        self.leaderboard_manager = Leaderboard() # Instantiate Leaderboard manager
        self.leaderboard_display = LeaderboardSprite(
            screen=self.screen,
            font_prompt=self.leaderboard_font_prompt,
            font_input=self.leaderboard_font_input,
            font_scores=self.leaderboard_font_scores,
            leaderboard_manager=self.leaderboard_manager,
            settings=settings_module # Pass the imported settings_module
        )

    def update_camera(self):
        self.camera.update(self.player) # Use Camera object

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
        weapon_name = "None"
        if self.player.weapon:
            weapon_name = self.player.weapon.name
        
        player_health = self.player.health
        player_kills = self.player.kills
        wave_status_text = self.wave_manager.get_wave_status_text()

        weapon_text = f"Weapon: {weapon_name}"
        health_text = f"Health: {player_health}"
        kills_text = f"Kills: {player_kills}"
        wave_text = f"Wave: {wave_status_text}"

        weapon_surface = self.font.render(weapon_text, True, BLACK)
        health_surface = self.font.render(health_text, True, BLACK)
        kills_surface = self.font.render(kills_text, True, BLACK)
        wave_surface = self.font.render(wave_text, True, BLACK)

        self.screen.blit(weapon_surface, (10, 10))
        self.screen.blit(health_surface, (10, 10 + weapon_surface.get_height() + 5))
        
        wave_text_width = wave_surface.get_width()
        self.screen.blit(wave_surface, (SCREEN_WIDTH - wave_text_width - 10, 10))
        
        kills_text_width = kills_surface.get_width()
        self.screen.blit(kills_surface, (SCREEN_WIDTH - kills_text_width - 10, 10 + wave_surface.get_height() + 5))

    def draw_minimap(self):
        map_x = SCREEN_WIDTH - MINIMAP_WIDTH - MINIMAP_MARGIN
        map_y = SCREEN_HEIGHT - MINIMAP_HEIGHT - MINIMAP_MARGIN

        minimap_surface = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT), pygame.SRCALPHA)
        minimap_surface.fill(MINIMAP_BG_COLOR)

        scale_x = MINIMAP_WIDTH / WORLD_WIDTH
        scale_y = MINIMAP_HEIGHT / WORLD_HEIGHT

        for room in self.rooms:
            mini_room_x = room.world_rect.x * scale_x
            mini_room_y = room.world_rect.y * scale_y
            mini_room_width = room.world_rect.width * scale_x
            mini_room_height = room.world_rect.height * scale_y
            
            pygame.draw.rect(minimap_surface, MINIMAP_ROOM_COLOR, 
                             (mini_room_x, mini_room_y, mini_room_width, mini_room_height))
            pygame.draw.rect(minimap_surface, MINIMAP_BORDER_COLOR,
                             (mini_room_x, mini_room_y, mini_room_width, mini_room_height), 1)

        player_mini_x = self.player.rect.centerx * scale_x
        player_mini_y = self.player.rect.centery * scale_y
        pygame.draw.circle(minimap_surface, MINIMAP_PLAYER_COLOR, 
                           (int(player_mini_x), int(player_mini_y)), 3)

        pygame.draw.rect(self.screen, MINIMAP_BORDER_COLOR, (map_x -1, map_y -1, MINIMAP_WIDTH + 2, MINIMAP_HEIGHT + 2), 1)
        self.screen.blit(minimap_surface, (map_x, map_y))

    def run(self):
        while self.running:
            if self.game_over:
                if not self.leaderboard_display.is_active:
                    self.leaderboard_display.activate(self.player.kills)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    action = self.leaderboard_display.handle_event(event)
                    if action == 'RESTART':
                        self.reset_game()
                        self.leaderboard_display.deactivate()
                    elif action == 'QUIT':
                        self.running = False
                
                self.leaderboard_display.update()
                self.leaderboard_display.draw()
                
                pygame.display.flip()
                self.clock.tick(FPS)
                continue
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE: 
                        if self.player.weapon.type == "ranged" or self.player.weapon.type == "grenade":
                            # Use entity_manager groups for player shoot method
                            self.player.shoot(self.entity_manager.projectiles, self.entity_manager.entities, self.entity_manager.npcs)
                        elif self.player.weapon.type == "melee":
                            attack_rect = self.player.melee_attack()
                            if attack_rect:
                                current_time = pygame.time.get_ticks()
                                self.melee_attack_visuals.append((attack_rect, current_time, MELEE_ATTACK_COLOR))
                                # Check for melee attack collisions with NPCs
                                for npc in self.entity_manager.npcs: # Use entity_manager group
                                    if attack_rect.colliderect(npc.rect):
                                        npc.take_damage(self.player.weapon.damage)
                                        print(f"Melee attack hit NPC for {self.player.weapon.damage} damage!")
                    elif event.key == pygame.K_1:
                        self.player.equip_weapon("pistol")
                    elif event.key == pygame.K_2:
                        self.player.equip_weapon("knife")
                    elif event.key == pygame.K_3:
                        self.player.equip_weapon("grenade_launcher")

            # Update entities - This will later be handled by specific systems (Movement, AI etc.)
            # For now, direct update calls for Player and NPC, other entities handled by entity_manager.update()
            self.player.update() # Player movement and input
            for npc in self.entity_manager.npcs: # Update NPCs specifically if they have complex updates
                 npc.update(self.player.rect, self.player) # NPC update needs player info
            
            # self.entity_manager.update(dt) # dt is not yet consistently used.
            # For other entities like projectiles, their update is simple and called if they are in entity_manager.entities
            # and the main loop below iterates through entity_manager.entities.
            # This part of update logic needs further refinement with systems.
            # For now, this loop updates projectiles, effects etc. if their update() takes no args.
            for entity in self.entity_manager.entities:
                if not isinstance(entity, (Player, NPC)): # Player and NPC already updated
                    entity.update()

            self.wave_manager.update() # WaveManager uses entity_manager.npcs
            
            if self.player.health <= 0 and not self.game_over:
                self.game_over = True

            # Projectile-NPC collisions using entity_manager groups
            for projectile in list(self.entity_manager.projectiles):
                hit_npcs = pygame.sprite.spritecollide(projectile, self.entity_manager.npcs, False) 
                if hit_npcs:
                    if isinstance(projectile, Grenade):
                        if not projectile.detonated:
                            # Grenade.explode() might need entity_manager or combat_manager later for AOE
                            projectile.explode(npcs_group=self.entity_manager.npcs, all_sprites_group=self.entity_manager.entities) 
                        # Grenade.kill() is called by its own explode or update logic
                        print(f"Grenade event processed (hit or detonated).")
                    else: # For regular projectiles
                        for npc in hit_npcs:
                            npc.take_damage(projectile.damage)
                            projectile.kill() # Remove projectile after hit
                            print(f"Projectile hit NPC for {projectile.damage} damage!")
                            break # Projectile hits one NPC and is destroyed
                            
            self.update_camera() 

            self.screen.fill(LIGHT_GRAY) 

            for room in self.rooms:
                room.draw(self.screen, self.camera.x, self.camera.y) # Use camera object's x, y
            
            # Draw NPC patrol areas and health bars using camera object's x, y
            for npc_sprite in self.entity_manager.npcs: # Use entity_manager group
                if not npc_sprite.is_following_player:
                    patrol_rect_world = pygame.Rect(
                        npc_sprite.patrol_limit_left, 
                        npc_sprite.rect.top,
                        npc_sprite.patrol_limit_right - npc_sprite.patrol_limit_left, 
                        npc_sprite.rect.height
                    )
                    # Use camera.x for offset
                    patrol_rect_screen_x = patrol_rect_world.x - self.camera.x 
                    patrol_rect_screen_y = patrol_rect_world.y - self.camera.y
                    pygame.draw.rect(self.screen, (255, 255, 0, 100), 
                                     (patrol_rect_screen_x, patrol_rect_screen_y, patrol_rect_world.width, patrol_rect_world.height), 1)

                if npc_sprite.is_following_player and npc_sprite.health > 0:
                    HEALTH_BAR_HEIGHT = 5
                    HEALTH_BAR_Y_OFFSET = 10
                    health_percentage = npc_sprite.health / npc_sprite.max_health
                    
                    bg_bar_width = npc_sprite.rect.width
                    bg_bar_x_world = npc_sprite.rect.x
                    bg_bar_y_world = npc_sprite.rect.top - HEALTH_BAR_Y_OFFSET
                    # Use camera.x, camera.y for offset
                    bg_bar_screen_x = bg_bar_x_world - self.camera.x
                    bg_bar_screen_y = bg_bar_y_world - self.camera.y
                    pygame.draw.rect(self.screen, (255, 0, 0), 
                                     (bg_bar_screen_x, bg_bar_screen_y, bg_bar_width, HEALTH_BAR_HEIGHT))

                    fg_bar_width = bg_bar_width * health_percentage
                    pygame.draw.rect(self.screen, (0, 255, 0), 
                                     (bg_bar_screen_x, bg_bar_screen_y, fg_bar_width, HEALTH_BAR_HEIGHT))

            # Draw all entities using camera.apply()
            for sprite in self.entity_manager.entities: # Use entity_manager group
                self.screen.blit(sprite.image, self.camera.apply(sprite.rect))

            current_time = pygame.time.get_ticks()
            for visual in list(self.melee_attack_visuals):
                rect, creation_time, color = visual
                if current_time - creation_time > MELEE_VISUAL_DURATION:
                    self.melee_attack_visuals.remove(visual)
                else:
                    temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    temp_surface.fill(color)
                    # Apply camera offset to melee visual's rect
                    self.screen.blit(temp_surface, self.camera.apply(rect))
            
            self.draw_radar()
            self.draw_status_bar()
            self.draw_minimap()
            pygame.display.flip() 
            self.clock.tick(FPS)

        pygame.quit()

    def reset_game(self):
        print("Resetting game...")
        self.game_over = False
        if self.leaderboard_display.is_active:
            self.leaderboard_display.deactivate()

        start_x = ROOM_WIDTH / 2
        start_y = ROOM_HEIGHT / 2
        # Player is an Entity, kill() removes from its groups (handled by entity_manager)
        if self.player: # Ensure player exists before trying to kill
            self.player.kill() 

        self.player = Player(start_x, start_y)
        self.entity_manager.add_entity(self.player, "player") # Add new player to entity_manager

        # Clear existing NPCs and Projectiles from entity_manager groups
        for npc in list(self.entity_manager.npcs): 
            npc.kill()
        for projectile in list(self.entity_manager.projectiles): 
            projectile.kill()
        self.melee_attack_visuals.clear()

        # Re-initialize WaveManager with entity_manager groups
        self.wave_manager = WaveManager(
            all_sprites_group=self.entity_manager.entities, 
            npcs_group=self.entity_manager.npcs,           
            player_reference=self.player
        )
        # Camera position is reset by its update method based on player
        self.update_camera() 

        print("Game has been reset.")
