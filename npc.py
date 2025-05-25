import pygame
import random # Import random
from settings import (
    NPC_WIDTH, NPC_HEIGHT, NPC_SPEED, NPC_COLOR, NPC_HEALTH, 
    NPC_DETECTION_RADIUS, NPC_CHASE_AREA_MULTIPLIER,
    NPC_PATROL_COLOR_HORIZONTAL, NPC_PATROL_COLOR_VERTICAL,
    HEALTH_PACK_DROP_CHANCE,
    NPC_MOVEMENT_RANGE, WORLD_WIDTH, WORLD_HEIGHT, # Added missing imports
    NPC_MELEE_COOLDOWN # NPC_MELEE_DAMAGE will be derived from weapon
)
from weapon import Weapon, WEAPON_DATA # Import Weapon and WEAPON_DATA
from attack_visual import AttackVisual # Import AttackVisual

class NPC(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, player_instance=None, all_sprites_group=None):
        super().__init__()
        self.image = pygame.Surface([NPC_WIDTH, NPC_HEIGHT])
        self.image.fill(NPC_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y
        self.start_x = start_x # Store initial position
        self.start_y = start_y
        self.all_sprites_group = all_sprites_group # Store the group for adding visuals

        self.speed = NPC_SPEED
        self.health = NPC_HEALTH
        self.max_health = NPC_HEALTH # Store max health
        self.movement_direction = pygame.math.Vector2(1, 0) # Initial movement direction (horizontal)
        self.movement_range = NPC_MOVEMENT_RANGE
        self.patrol_limit_left = self.start_x - self.movement_range
        self.patrol_limit_right = self.start_x + self.movement_range
        self.detection_radius = NPC_DETECTION_RADIUS
        self.is_following_player = False
        self.player_instance = player_instance # Store player instance
        self.last_melee_attack_time = 0 # For NPC melee cooldown

        # Equip NPC with a knife by default
        if "knife" in WEAPON_DATA:
            self.weapon = Weapon(**WEAPON_DATA["knife"])
            print(f"NPC equipped {self.weapon.name}.")
        else:
            # Fallback or error if knife is not defined, though it should be
            self.weapon = None 
            print("Warning: Knife not found in WEAPON_DATA for NPC. NPC will be unarmed.")

    def update(self, player_rect, player_object): # Added player_object for dealing damage
        distance_to_player = pygame.math.Vector2(player_rect.centerx - self.rect.centerx, 
                                                 player_rect.centery - self.rect.centery).length()
        direction_to_player = pygame.math.Vector2(0,0)
        if distance_to_player > 0:
            direction_to_player = pygame.math.Vector2(player_rect.centerx - self.rect.centerx, 
                                                    player_rect.centery - self.rect.centery).normalize()

        if distance_to_player <= self.detection_radius:
            self.is_following_player = True
        else:
            if self.is_following_player:
                self.is_following_player = False 

        if self.is_following_player:
            move_vector = pygame.math.Vector2(player_rect.centerx - self.rect.centerx, 
                                              player_rect.centery - self.rect.centery)
            if move_vector.length_squared() > 0:
                move_vector = move_vector.normalize()
                self.rect.x += move_vector.x * self.speed
                self.rect.y += move_vector.y * self.speed

            # Check for melee attack range and cooldown
            attack_range = (self.rect.width / 2) + (player_rect.width / 2) + 5 # 5 pixels buffer
            # Use weapon range if available, otherwise use the calculated attack_range
            effective_attack_range = getattr(self.weapon, 'range', attack_range) if self.weapon else attack_range

            if distance_to_player <= effective_attack_range and self.weapon and self.weapon.type == "melee": # Check if armed with melee
                current_time = pygame.time.get_ticks()
                # Use weapon's fire_rate for attack cooldown if available, else default
                attack_cooldown = self.weapon.fire_rate * 1000 if hasattr(self.weapon, 'fire_rate') else NPC_MELEE_COOLDOWN
                
                if current_time - self.last_melee_attack_time > attack_cooldown:
                    self.last_melee_attack_time = current_time
                    player_object.take_damage(self.weapon.damage) # Use weapon's damage
                    print(f"NPC attacked player with {self.weapon.name} for {self.weapon.damage} damage!")
                    # Create attack visual
                    if self.all_sprites_group is not None and hasattr(self.weapon, 'range'):
                        # Visual properties
                        visual_length = self.weapon.range 
                        visual_thickness = 10 # Or some other value, maybe based on weapon
                        # Position the visual slightly in front of the NPC, centered on the attack direction
                        offset_distance = self.rect.width / 2 # Start visual from edge of NPC
                        visual_center_x = self.rect.centerx + direction_to_player.x * (offset_distance + visual_length / 2)
                        visual_center_y = self.rect.centery + direction_to_player.y * (offset_distance + visual_length / 2)
                        
                        attack_vis = AttackVisual(
                            center_pos=(visual_center_x, visual_center_y),
                            width=visual_length, 
                            height=visual_thickness,
                            direction_vector=direction_to_player
                        )
                        self.all_sprites_group.add(attack_vis)
        else:
            # Original patrol behavior (horizontal movement)
            self.rect.x += self.movement_direction.x * self.speed
            # Check if NPC has moved beyond its allowed range from the start_x
            if self.movement_direction.x == 1 and self.rect.x >= self.patrol_limit_right:
                self.movement_direction.x = -1 # Change direction to left
                self.rect.x = self.patrol_limit_right # Clamp to boundary
            elif self.movement_direction.x == -1 and self.rect.x <= self.patrol_limit_left:
                self.movement_direction.x = 1 # Change direction to right
                self.rect.x = self.patrol_limit_left # Clamp to boundary
        
        # Keep NPC within world boundaries
        self.rect.clamp_ip(pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))

    def take_damage(self, amount):
        self.health -= amount
        print(f"NPC took {amount} damage, health is now {self.health}")
        if self.health <= 0:
            print("NPC died")
            if self.player_instance: # Check if player_instance is set
                self.player_instance.increment_kills()
            self.kill() # Remove NPC from all sprite groups
            # Potentially drop an item here
            if random.random() < HEALTH_PACK_DROP_CHANCE:
                # Need to know where to add the health pack (e.g., an items group in Game)
                print(f"NPC dropped a health pack at ({self.rect.centerx}, {self.rect.centery})!")
                # game_instance.spawn_health_pack(self.rect.centerx, self.rect.centery)
                # This part needs the Game instance or a callback to spawn items.
                # For now, we'll just print.
                # To properly implement, the Game class should handle item spawning and groups.
                pass # Placeholder for actual item spawning
