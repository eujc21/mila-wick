import pygame
import random
from npc import NPC
from item import HealthPack # Import HealthPack
from settings import (
    WORLD_ROOM_COLS, ROOM_WIDTH, WORLD_ROOM_ROWS, ROOM_HEIGHT, 
    NPC_WIDTH, NPC_HEIGHT, NPC_DETECTION_RADIUS, NPC_CHASE_AREA_MULTIPLIER, ITEM_SIZE 
)

class WaveManager:
    def __init__(self, game_instance):
        self.game = game_instance  # Reference to the main game instance
        self.wave_number = 0
        # self.npcs_per_wave_base = 10  # Starting number of NPCs - Replaced by Fibonacci
        self.npcs_to_spawn_this_wave = 0
        self.wave_active = False
        self.time_between_waves = 1000  # 1 second in milliseconds
        self.last_wave_end_time = 0
        self.initial_delay_passed = False # To handle delay before first wave
        # Fibonacci sequence tracking
        # self.fib_a = 1  # F(1) - Previous values, will be effectively set by initial wave values
        # self.fib_b = 1  # F(2) - Previous values
        self.initial_npcs_wave_1 = 21 # Wave 1 starts with 21 NPCs
        self.initial_npcs_wave_2 = 34 # Wave 2 will have 34 NPCs (21+13, or F(n) after F(n-1)=21)

    def _get_spawn_location(self, player_rect):
        min_dist_from_player = 150  # pixels
        max_attempts = 20
        
        world_w = WORLD_ROOM_COLS * ROOM_WIDTH
        world_h = WORLD_ROOM_ROWS * ROOM_HEIGHT

        # Ensure spawn range is valid
        spawn_x_min = 0
        spawn_x_max = max(spawn_x_min, world_w - NPC_WIDTH)
        spawn_y_min = 0
        spawn_y_max = max(spawn_y_min, world_h - NPC_HEIGHT)

        if spawn_x_min > spawn_x_max or spawn_y_min > spawn_y_max:
            print("Warning: World too small for NPC dimensions in WaveManager spawn. Spawning at center.")
            return world_w / 2, world_h / 2

        for _ in range(max_attempts):
            spawn_x = random.randint(spawn_x_min, spawn_x_max)
            spawn_y = random.randint(spawn_y_min, spawn_y_max)

            # Check distance from player's center to NPC's potential top-left
            dist_to_player = pygame.math.Vector2(spawn_x - player_rect.centerx, 
                                                 spawn_y - player_rect.centery).length()
            
            if dist_to_player > min_dist_from_player:
                return spawn_x, spawn_y
        
        # Fallback if too many attempts to find a distant spot
        return random.randint(spawn_x_min, spawn_x_max), random.randint(spawn_y_min, spawn_y_max)

    def start_next_wave(self):
        self.wave_number += 1
        self.wave_active = True

        if self.wave_number == 1:
            self.npcs_to_spawn_this_wave = self.initial_npcs_wave_1
            self.fib_a = 1 # Reset for sequence starting from F(3) effectively
            self.fib_b = 1 
        elif self.wave_number == 2:
            self.npcs_to_spawn_this_wave = self.initial_npcs_wave_2
            self.fib_a = self.initial_npcs_wave_1 # F(1) for next calculation
            self.fib_b = self.initial_npcs_wave_2 # F(2) for next calculation
        else:
            # Calculate next Fibonacci number for NPCs
            # F(n) = F(n-1) + F(n-2)
            # Our wave_number is effectively 'n'.
            # For wave 3, we need F(3) = F(2) + F(1) = fib_b + fib_a
            next_fib = self.fib_a + self.fib_b
            self.npcs_to_spawn_this_wave = next_fib
            self.fib_a = self.fib_b # Update F(n-2) to previous F(n-1)
            self.fib_b = next_fib   # Update F(n-1) to current F(n)
        
        # Ensure a minimum number of NPCs if Fibonacci sequence is too low initially or for very early waves
        min_npcs_for_any_wave = 1 
        self.npcs_to_spawn_this_wave = max(self.npcs_to_spawn_this_wave, min_npcs_for_any_wave)

        print(f"Starting Wave {self.wave_number} with {self.npcs_to_spawn_this_wave} NPCs (Fibonacci).")

        # Spawn NPCs
        world_w = WORLD_ROOM_COLS * ROOM_WIDTH
        world_h = WORLD_ROOM_ROWS * ROOM_HEIGHT
        spawn_x_min = 0
        spawn_x_max = max(spawn_x_min, world_w - NPC_WIDTH)
        spawn_y_min = 0
        spawn_y_max = max(spawn_y_min, world_h - NPC_HEIGHT)

        for _ in range(self.npcs_to_spawn_this_wave):
            spawn_x, spawn_y = self._get_spawn_location(self.game.player.rect)
            npc = NPC(spawn_x, spawn_y)
            self.game.all_sprites.add(npc)
            self.game.npcs.add(npc)
        
        # Spawn a health pack for the new wave
        item_spawn_x_max = max(0, world_w - ITEM_SIZE[0])
        item_spawn_y_max = max(0, world_h - ITEM_SIZE[1])
        
        if item_spawn_x_max > 0 and item_spawn_y_max > 0: 
            health_pack_x, health_pack_y = self._get_spawn_location(self.game.player.rect) 
            health_pack_x = max(0, min(health_pack_x, world_w - ITEM_SIZE[0]))
            health_pack_y = max(0, min(health_pack_y, world_h - ITEM_SIZE[1]))

            health_pack = HealthPack(health_pack_x, health_pack_y)
            self.game.all_sprites.add(health_pack)
            self.game.items.add(health_pack) 
            print(f"Spawned HealthPack at ({health_pack_x}, {health_pack_y}) for Wave {self.wave_number}")
        else:
            print(f"Could not spawn HealthPack for Wave {self.wave_number} due to world size or item size constraints.")

        if self.npcs_to_spawn_this_wave == 0 and (spawn_x_min > spawn_x_max or spawn_y_min > spawn_y_max):
             # Handles case where world is too small and no NPCs could be prepared
             print("Could not spawn NPCs for the wave due to world size constraints.")
             self.wave_active = False # Cannot proceed with an empty wave if spawning failed

    def update(self):
        current_time = pygame.time.get_ticks()

        if not self.initial_delay_passed:
            if self.last_wave_end_time == 0: # Set for the very first delay
                 self.last_wave_end_time = current_time 
            if current_time - self.last_wave_end_time > self.time_between_waves / 2: # Shorter delay for the first wave
                self.initial_delay_passed = True
                self.last_wave_end_time = current_time # Reset for next wave timing
                self.start_next_wave()
            return

        if not self.wave_active:
            # Check if all NPCs from previous wave are cleared
            if not self.game.npcs:  # No NPCs left in the group
                if current_time - self.last_wave_end_time > self.time_between_waves:
                    self.start_next_wave()
        else:
            # Wave is active, check if all NPCs are defeated
            if not self.game.npcs: 
                print(f"Wave {self.wave_number} cleared!")
                self.wave_active = False
                self.last_wave_end_time = current_time
