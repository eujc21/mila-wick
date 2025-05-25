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
# from attack_visual import AttackVisual # Old import, AttackVisual is now in game.utils.effects
from game.utils.effects import AttackVisual # New import for AttackVisual
from game.core.entity import Entity # Import Entity

class NPC(Entity): # Inherit from Entity
    def __init__(self, start_x, start_y, event_manager=None): # event_manager added
        super().__init__(x=start_x, y=start_y, health=NPC_HEALTH) # Call Entity's __init__
        self.image = pygame.Surface([NPC_WIDTH, NPC_HEIGHT])
        self.image.fill(NPC_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y
        self.start_x = start_x # Store initial position
        self.start_y = start_y
        # self.all_sprites_group = all_sprites_group # Removed
        self.event_manager = event_manager # Store event_manager

        self.speed = NPC_SPEED
        # self.health = NPC_HEALTH # Removed, handled by Entity
        # self.max_health = NPC_HEALTH # Removed, handled by Entity
        self.movement_direction = pygame.math.Vector2(1, 0) # Initial movement direction (horizontal)
        self.movement_range = NPC_MOVEMENT_RANGE
        self.patrol_limit_left = self.start_x - self.movement_range
        self.patrol_limit_right = self.start_x + self.movement_range
        self.detection_radius = NPC_DETECTION_RADIUS
        self.is_following_player = False
        # self.player_instance = player_instance # Removed
        # self.last_melee_attack_time = 0 # Removed, WeaponSystem handles cooldowns

        # Equip NPC with a knife by default
        if "knife" in WEAPON_DATA:
            self.weapon = Weapon(**WEAPON_DATA["knife"])
            print(f"NPC equipped {self.weapon.name}.")
        else:
            # Fallback or error if knife is not defined, though it should be
            self.weapon = None 
            print("Warning: Knife not found in WEAPON_DATA for NPC. NPC will be unarmed.")

    def update(self, entity_manager, combat_manager, effect_manager, weapon_system): # weapon_system added
        players = entity_manager.players.sprites()
        player_sprite = None
        if players:
            player_sprite = players[0] # Assuming single player

        if player_sprite:
            player_rect = player_sprite.rect
            distance_to_player = pygame.math.Vector2(player_rect.centerx - self.rect.centerx, 
                                                     player_rect.centery - self.rect.centery).length()
            direction_to_player = pygame.math.Vector2(0,0)
            if distance_to_player > 0:
                direction_to_player = pygame.math.Vector2(player_rect.centerx - self.rect.centerx, 
                                                        player_rect.centery - self.rect.centery).normalize()

            if distance_to_player <= self.detection_radius:
                self.is_following_player = True
            # Removed 'else' part that sets is_following_player to False if player is outside detection_radius
            # This state should persist until player is outside a larger chase_area or NPC loses line of sight.
            # For now, if player gets out of detection_radius, NPC stops following immediately.
            # This can be refined later with a chase_area_radius check. Example:
            # chase_area_radius = self.detection_radius * NPC_CHASE_AREA_MULTIPLIER 
            # if distance_to_player > chase_area_radius: self.is_following_player = False
            else: # Player is outside detection radius
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
                effective_attack_range = getattr(self.weapon, 'range', attack_range) if self.weapon else attack_range

                if distance_to_player <= effective_attack_range and self.weapon and self.weapon.type == "melee":
                    # Melee attack logic now handled by WeaponSystem
                    # Cooldown, damage dealing, and visual effect creation are managed by weapon_system.use_weapon
                    weapon_system.use_weapon(self, target_info=player_sprite)
                    # Old logic for direct cooldown check, combat_manager call, and effect_manager call is removed.
        else: # No player_sprite found
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

    # take_damage method removed, inherited from Entity

    def kill(self):
        # Custom NPC death logic
        print(f"NPC at ({self.rect.x}, {self.rect.y}) is being killed.") # For debugging
        # Removed player kill count increment from here
        
        # Emit NPC_DIED_EVENT
        if self.event_manager:
            self.event_manager.emit("NPC_DIED_EVENT", {"npc_id": id(self), "position": self.rect.center})

        # Placeholder for item drop, using existing random chance from original take_damage
        if random.random() < HEALTH_PACK_DROP_CHANCE: # HEALTH_PACK_DROP_CHANCE is imported from settings
            print(f"NPC dropped a health pack at ({self.rect.centerx}, {self.rect.centery})!")
            # Actual item spawning logic will be integrated later via a manager or event.

        # Call the superclass's kill method to handle removal from sprite groups
        super().kill()
