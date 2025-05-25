import pygame
import random
from game.entities.npc import NPC # Changed import path
# Removed: from item import HealthPack
from game.core.settings import ( # Changed import path
    WORLD_ROOM_COLS, ROOM_WIDTH, WORLD_ROOM_ROWS, ROOM_HEIGHT, 
    NPC_WIDTH, NPC_HEIGHT, NPC_DETECTION_RADIUS, NPC_CHASE_AREA_MULTIPLIER, ITEM_SIZE, WAVE_REST_TIME
)

class WaveManager:
    def __init__(self, entity_manager, player_reference, event_manager=None): # event_manager added
        self.entity_manager = entity_manager # Store entity_manager
        self.event_manager = event_manager # Store event_manager
        # self.all_sprites and self.npcs attributes removed
        self.player_ref = player_reference # Store player reference
        
        # Start at wave 8 (where NPC count is 21)
        self.current_wave_number = 7 # Will be incremented to 8 on first call to start_next_wave
        self.npcs_to_spawn_this_wave = 0
        self.wave_active = False
        self.time_between_waves = 1000  # 1 second in milliseconds (used for initial delay logic)
        self.last_wave_end_time = 0
        self.initial_delay_passed = False # To handle delay before first wave
        self.rest_period = WAVE_REST_TIME
        
        # Fibonacci sequence tracking, adjusted for starting at wave 8 (F(8) = 21 NPCs)
        # For wave k > 2, npc_count = fib_a + fib_b. fib_a is F(k-2), fib_b is F(k-1)
        # For first wave being 8 (k=8):
        # fib_a should be F(6) = 8
        # fib_b should be F(7) = 13
        self.fib_a = 8 
        self.fib_b = 13

        # Start the first wave (wave 8) almost immediately by setting last_wave_end_time appropriately
        self.last_wave_end_time = pygame.time.get_ticks() - self.rest_period 
        # This ensures the first call to update() will likely trigger start_next_wave()

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
        self.current_wave_number += 1
        self.wave_active = True
        
        # Calculate NPC count using Fibonacci sequence
        if self.current_wave_number == 1:
            npc_count = 1
            self.fib_a = 0 # Reset for sequence: 0, 1, 1, 2, 3, 5...
            self.fib_b = 1
        elif self.current_wave_number == 2:
            npc_count = 1 # Second wave also has 1
            self.fib_a = 1
            self.fib_b = 1
        else:
            # Next Fibonacci number
            npc_count = self.fib_a + self.fib_b
            self.fib_a, self.fib_b = self.fib_b, npc_count # Update sequence

        # Ensure at least 1 NPC if fib somehow results in 0 for later waves (should not happen with proper sequence)
        if npc_count == 0 and self.current_wave_number > 1: 
            npc_count = 1

        # Store the number of NPCs to spawn for this wave, to be used by the loop below
        self.npcs_to_spawn_this_wave = npc_count

        print(f"Starting Wave {self.current_wave_number} with {self.npcs_to_spawn_this_wave} NPCs.")
        # self.spawn_npcs(npc_count) # This call seems redundant if the loop below does the spawning

        # Spawn NPCs
        world_w = WORLD_ROOM_COLS * ROOM_WIDTH
        world_h = WORLD_ROOM_ROWS * ROOM_HEIGHT
        spawn_x_min = 0
        spawn_x_max = max(spawn_x_min, world_w - NPC_WIDTH)
        spawn_y_min = 0
        spawn_y_max = max(spawn_y_min, world_h - NPC_HEIGHT)

        for _ in range(self.npcs_to_spawn_this_wave):
            spawn_x, spawn_y = self._get_spawn_location(self.player_ref.rect)
            # all_sprites_group argument removed from NPC constructor, pass event_manager
            npc = NPC(spawn_x, spawn_y, event_manager=self.event_manager) 
            self.entity_manager.add_entity(npc, "npc") # Add NPC via entity_manager
        
        if self.npcs_to_spawn_this_wave == 0 and (spawn_x_min > spawn_x_max or spawn_y_min > spawn_y_max):
             # Handles case where world is too small and no NPCs could be prepared
             print("Could not spawn NPCs for the wave due to world size constraints.")
             self.wave_active = False # Cannot proceed with an empty wave if spawning failed

    def spawn_npcs(self, count):
        for _ in range(count):
            # Spawn at random locations across the world, trying to avoid player's immediate vicinity
            # This is a simple approach; more sophisticated spawning might consider player location,
            # specific spawn points per room, or ensuring NPCs are off-screen.
            
            # For now, random world coordinates:
            spawn_x = random.randint(0, WORLD_ROOM_COLS * ROOM_WIDTH)
            spawn_y = random.randint(0, WORLD_ROOM_ROWS * ROOM_HEIGHT)
            
            # Basic check to avoid spawning too close to (0,0) if it's the player start
            # This is a placeholder for better logic.
            # A robust solution would get player's current position.
            if abs(spawn_x - ROOM_WIDTH/2) < ROOM_WIDTH/4 and abs(spawn_y - ROOM_HEIGHT/2) < ROOM_HEIGHT/4 and self.current_wave_number < 3:
                 # Try to push them to a neighboring area if too close to initial player zone
                if random.choice([True, False]):
                    spawn_x += random.choice([-1, 1]) * ROOM_WIDTH
                else:
                    spawn_y += random.choice([-1, 1]) * ROOM_HEIGHT
                
                # Clamp to world boundaries after adjustment
                spawn_x = max(0, min(spawn_x, WORLD_ROOM_COLS * ROOM_WIDTH))
                spawn_y = max(0, min(spawn_y, WORLD_ROOM_ROWS * ROOM_HEIGHT))

            # all_sprites_group argument removed from NPC constructor, pass event_manager
            npc = NPC(spawn_x, spawn_y, event_manager=self.event_manager) 
            self.entity_manager.add_entity(npc, "npc") # Add NPC via entity_manager
            
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
            if not self.entity_manager.npcs:  # Use entity_manager.npcs
                if current_time - self.last_wave_end_time > self.rest_period: # Use self.rest_period
                    self.start_next_wave()
        else:
            # Wave is active, check if all NPCs are defeated
            if not self.entity_manager.npcs: # Use entity_manager.npcs
                print(f"Wave {self.current_wave_number} cleared!")
                self.wave_active = False
                self.last_wave_end_time = current_time

    def get_wave_number(self):
        return self.current_wave_number

    def get_wave_status_text(self):
        if self.wave_active:
            return f"Wave: {self.current_wave_number} (Active - {len(self.entity_manager.npcs)} left)" # Use entity_manager.npcs
        else:
            time_to_next_wave = (self.rest_period - (pygame.time.get_ticks() - self.last_wave_end_time)) / 1000
            return f"Wave: {self.current_wave_number} (Resting - Next in {max(0, time_to_next_wave):.1f}s)"
