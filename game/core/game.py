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
from game.utils.effects import EffectManager # Import EffectManager
from game.systems.weapon_system import WeaponSystem # Import WeaponSystem
from game.core.event_manager import EventManager # Import EventManager

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
        self.effect_manager = EffectManager() # Instantiate EffectManager
        self.weapon_system = WeaponSystem(self.entity_manager, self.effect_manager, self.combat_manager) # Instantiate WeaponSystem
        self.event_manager = EventManager() # Instantiate EventManager
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
        self.wave_manager = WaveManager(self.entity_manager, self.player, self.event_manager) # Pass event_manager
        
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
        
        # Subscribe to events
        self.event_manager.subscribe("NPC_DIED_EVENT", self.handle_npc_killed)

    def handle_npc_killed(self, event_data):
        # Assuming self.player is valid and has increment_kills method
        if self.player and hasattr(self.player, 'increment_kills'):
            self.player.increment_kills()
            print(f"Game: Player kills updated to {self.player.kills} via NPC_DIED_EVENT. Event data: {event_data}")
        else:
            print(f"Game: Player or increment_kills method not found. Cannot update kills for NPC_DIED_EVENT.")

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
                        # Player attack logic now handled by WeaponSystem
                        self.weapon_system.use_weapon(self.player)
                        # Old logic for player.shoot and player.melee_attack, including melee visual creation, is removed.
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
                 npc.update(self.entity_manager, self.combat_manager, self.effect_manager, self.weapon_system) # Pass weapon_system
            
            # Update EffectManager
            self.effect_manager.update() # Call EffectManager's update

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

            # Call EntityManager to handle collisions, passing EffectManager
            self.entity_manager.handle_collisions(self.effect_manager)
            # The projectile-NPC collision loop has been moved to EntityManager.handle_collisions()
                            
            self.update_camera() 

            self.screen.fill(LIGHT_GRAY) 

            for room in self.rooms:
                room.draw(self.screen, self.camera.x, self.camera.y) # Use camera object's x, y
            
            # Draw NPC patrol paths and health bars using camera object's x, y
            for npc_sprite in self.entity_manager.npcs:  # Use entity_manager group
                if not npc_sprite.is_following_player:
                    # Draw a line between every pair of waypoints (all possible connections)
                    points = [(x - self.camera.x, y - self.camera.y) for (x, y) in npc_sprite.patrol_points]
                    for i in range(len(points)):
                        for j in range(i + 1, len(points)):
                            pygame.draw.line(self.screen, (255, 165, 0), points[i], points[j], 1)
                    # Draw small circles at each waypoint for visibility
                    for px, py in points:
                        pygame.draw.circle(self.screen, (255, 165, 0), (int(px), int(py)), 5, 1)

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
            
            # Draw effects managed by EffectManager
            self.effect_manager.draw(self.screen, self.camera)

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
        self.effect_manager.effects.empty() # Clear existing effects
        # Re-initialize EffectManager (optional, emptying might suffice)
        # self.effect_manager = EffectManager() 


        # Re-initialize WaveManager with entity_manager groups
        self.wave_manager = WaveManager(self.entity_manager, self.player) # Already updated
        # Camera position is reset by its update method based on player
        self.update_camera() 

        print("Game has been reset.")
