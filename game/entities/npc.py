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
        super().__init__(x=start_x, y=start_y, health=NPC_HEALTH) # Call Entity's __init__
        self.image = pygame.Surface([NPC_WIDTH, NPC_HEIGHT])
        self.image.fill(NPC_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y
        self.start_x = start_x # Store initial position
        self.start_y = start_y
        self.event_manager = event_manager # Store event_manager

        self.speed = NPC_SPEED
        self.base_speed = NPC_SPEED # For human-like variation
        self.movement_direction = pygame.math.Vector2(1, 0) # Initial movement direction for patrol
        self.direction = pygame.math.Vector2(1, 0) # Initial facing direction, matches patrol
        self.movement_range = NPC_MOVEMENT_RANGE
        self.patrol_limit_left = self.start_x - self.movement_range
        self.patrol_limit_right = self.start_x + self.movement_range
        self.detection_radius = NPC_DETECTION_RADIUS
        self.is_following_player = False

        # --- Human-like patrol variables ---
        # Define patrol waypoints; spread them for a larger, more interesting area
        self.patrol_points = [
            (self.start_x, self.start_y),
            (self.start_x + 150, self.start_y + 60),
            (self.start_x + 300, self.start_y - 80),
            (self.start_x + 80, self.start_y + 170)
        ]
        self.current_patrol_index = 0
        self.patrol_pause_until = 0 # Time to pause until (pygame.time.get_ticks())
        # -------------------------------

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
            player_sprite = players[0]  # Assuming single player

        if player_sprite:
            player_rect = player_sprite.rect
            vec_to_player = pygame.math.Vector2(player_rect.centerx - self.rect.centerx, 
                                                player_rect.centery - self.rect.centery)
            distance_to_player = vec_to_player.length()
            direction_to_player = pygame.math.Vector2(0, 0)
            if distance_to_player > 0:
                direction_to_player = vec_to_player.normalize()

            # Activate following if player is close enough
            if not self.is_following_player and distance_to_player <= self.detection_radius:
                self.is_following_player = True

            if self.is_following_player:
                if direction_to_player.length_squared() > 0:
                    self.direction = direction_to_player

                # Move towards player
                self.rect.x += self.direction.x * self.speed
                self.rect.y += self.direction.y * self.speed

                # Check melee attack range and cooldown
                attack_range = (self.rect.width / 2) + (player_rect.width / 2) + 5  # 5 pixels buffer
                effective_attack_range = getattr(self.weapon, 'range', attack_range) if self.weapon else attack_range

                if distance_to_player <= effective_attack_range and self.weapon and self.weapon.type == "melee":
                    weapon_system.use_weapon(self, target_info=player_sprite)
            else:
                # Player is too far, so patrol
                self._patrol()
        else:
            # No player found, patrol
            self._patrol()

        # Keep NPC within world boundaries
        self.rect.clamp_ip(pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT))

        # --- NPC-NPC collision (prevents overlap) ---
        for other_npc in entity_manager.npcs:
            if other_npc is not self and self.rect.colliderect(other_npc.rect):
                dx = self.rect.centerx - other_npc.rect.centerx
                dy = self.rect.centery - other_npc.rect.centery
                if dx == 0 and dy == 0:
                    dx, dy = 1, 1  # Prevent division by zero
                overlap_x = (self.rect.width // 2 + other_npc.rect.width // 2) - abs(dx)
                overlap_y = (self.rect.height // 2 + other_npc.rect.height // 2) - abs(dy)
                if overlap_x > 0 and abs(dx) > abs(dy):
                    self.rect.x += (overlap_x if dx > 0 else -overlap_x) // 2
                elif overlap_y > 0:
                    self.rect.y += (overlap_y if dy > 0 else -overlap_y) // 2

    def _patrol(self):
        """Human-like patrol: moves between multiple waypoints with natural pauses and speed variation."""
        now = pygame.time.get_ticks()
        if now < self.patrol_pause_until:
            # Still pausing at this waypoint (simulate looking around)
            return

        # Current target waypoint
        target_x, target_y = self.patrol_points[self.current_patrol_index]
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Human-like speed variation
        speed = self.base_speed * random.uniform(0.9, 1.12)

        if distance < 6:
            # Arrived at waypoint: pause for a short, random time
            self.patrol_pause_until = now + random.randint(600, 1800)  # pause 0.6-1.8 seconds
            # Pick a new random waypoint (not the same as before)
            next_index = self.current_patrol_index
            while next_index == self.current_patrol_index and len(self.patrol_points) > 1:
                next_index = random.randint(0, len(self.patrol_points) - 1)
            self.current_patrol_index = next_index
        else:
            direction = pygame.math.Vector2(dx, dy)
            if direction.length() > 0:
                direction = direction.normalize()
                self.rect.x += direction.x * speed
                self.rect.y += direction.y * speed
                self.direction = direction

    def take_damage(self, amount, source=None):
        super().take_damage(amount)
        self.is_following_player = True  # Start pursuing player if damaged

    def kill(self):
        # Custom NPC death logic
        print(f"NPC at ({self.rect.x}, {self.rect.y}) is being killed.") # For debugging
        
        # Emit NPC_DIED_EVENT
        if self.event_manager:
            self.event_manager.emit("NPC_DIED_EVENT", {"npc_id": id(self), "position": self.rect.center})

        # Placeholder for item drop, using existing random chance from original take_damage
        if random.random() < HEALTH_PACK_DROP_CHANCE: # HEALTH_PACK_DROP_CHANCE is imported from settings
            print(f"NPC dropped a health pack at ({self.rect.centerx}, {self.rect.centery})!")
            # Actual item spawning logic will be integrated later via a manager or event.

        # Call the superclass's kill method to handle removal from sprite groups
        super().kill()