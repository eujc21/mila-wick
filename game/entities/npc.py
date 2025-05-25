import pygame
import random
# Import settings from the correct path
from game.core.settings import (
    NPC_WIDTH, NPC_HEIGHT, NPC_SPEED, NPC_COLOR, NPC_MOVEMENT_RANGE, 
    NPC_HEALTH, NPC_DETECTION_RADIUS, NPC_CHASE_AREA_MULTIPLIER,
    NPC_PATROL_COLOR_HORIZONTAL, NPC_PATROL_COLOR_VERTICAL,
    NPC_MELEE_COOLDOWN, ROOM_WIDTH, ROOM_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT,
    HEALTH_PACK_DROP_CHANCE # Added HEALTH_PACK_DROP_CHANCE
)
from game.core.entity import Entity # Corrected import for Entity
from game.utils.weapon import Weapon, WEAPON_DATA # Corrected import for Weapon and WEAPON_DATA
from game.utils.effects import AttackVisual # New import for AttackVisual

class NPC(Entity): # Inherit from Entity
    def __init__(self, start_x, start_y, event_manager=None): # event_manager added
        super().__init__(x=start_x, y=start_y, health=NPC_HEALTH) # Call Entity\'s __init__
        self.image = pygame.Surface([NPC_WIDTH, NPC_HEIGHT])
        self.image.fill(NPC_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y
        self.start_x = start_x # Store initial position
        self.start_y = start_y
        self.event_manager = event_manager # Store event_manager

        self.speed = NPC_SPEED
        self.movement_direction = pygame.math.Vector2(1, 0) # Initial movement direction for patrol
        self.direction = pygame.math.Vector2(1, 0) # Initial facing direction, matches patrol
        self.movement_range = NPC_MOVEMENT_RANGE
        self.patrol_limit_left = self.start_x - self.movement_range
        self.patrol_limit_right = self.start_x + self.movement_range
        self.detection_radius = NPC_DETECTION_RADIUS
        self.is_following_player = False

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
            vec_to_player = pygame.math.Vector2(player_rect.centerx - self.rect.centerx, 
                                                player_rect.centery - self.rect.centery)
            distance_to_player = vec_to_player.length()
            direction_to_player = pygame.math.Vector2(0,0)
            if distance_to_player > 0:
                direction_to_player = vec_to_player.normalize()

            # Determine if following player (simplified logic for now)
            # Consider chase_area_radius for more persistent following later
            if distance_to_player <= self.detection_radius:
                self.is_following_player = True
            else: 
                self.is_following_player = False

            if self.is_following_player:
                if direction_to_player.length_squared() > 0:
                    self.direction = direction_to_player # Update facing direction
                
                # Movement towards player
                self.rect.x += self.direction.x * self.speed
                self.rect.y += self.direction.y * self.speed

                # Check for melee attack range and cooldown
                attack_range = (self.rect.width / 2) + (player_rect.width / 2) + 5 # 5 pixels buffer
                effective_attack_range = getattr(self.weapon, 'range', attack_range) if self.weapon else attack_range

                if distance_to_player <= effective_attack_range and self.weapon and self.weapon.type == "melee":
                    weapon_system.use_weapon(self, target_info=player_sprite)
            else: # Player exists, but not following (e.g., too far)
                self._patrol()
        else: # No player_sprite found
            self._patrol()
        
        # Keep NPC within world boundaries
        self.rect.clamp_ip(pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))

    def _patrol(self):
        """Handles NPC patrol behavior and updates facing direction."""
        self.rect.x += self.movement_direction.x * self.speed
        self.direction = pygame.math.Vector2(self.movement_direction.x, 0) # Update facing for patrol

        if self.movement_direction.x == 1 and self.rect.x >= self.patrol_limit_right:
            self.movement_direction.x = -1 
            self.direction.x = -1 # Keep direction consistent
            self.rect.x = self.patrol_limit_right # Clamp to boundary
        elif self.movement_direction.x == -1 and self.rect.x <= self.patrol_limit_left:
            self.movement_direction.x = 1 
            self.direction.x = 1 # Keep direction consistent
            self.rect.x = self.patrol_limit_left # Clamp to boundary

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
