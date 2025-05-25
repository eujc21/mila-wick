import pygame
import random # Import random
from settings import (
    NPC_WIDTH, NPC_HEIGHT, NPC_SPEED, NPC_COLOR, NPC_HEALTH, 
    NPC_DETECTION_RADIUS, NPC_CHASE_AREA_MULTIPLIER,
    NPC_PATROL_COLOR_HORIZONTAL, NPC_PATROL_COLOR_VERTICAL,
    HEALTH_PACK_DROP_CHANCE,
    NPC_MOVEMENT_RANGE, WORLD_WIDTH, WORLD_HEIGHT # Added missing imports
)

class NPC(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, player_instance=None):
        super().__init__()
        self.image = pygame.Surface([NPC_WIDTH, NPC_HEIGHT])
        self.image.fill(NPC_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y
        self.start_x = start_x # Store initial position
        self.start_y = start_y

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

    def update(self, player_rect): # Player's rect is needed for follow logic
        distance_to_player = pygame.math.Vector2(player_rect.centerx - self.rect.centerx, 
                                                 player_rect.centery - self.rect.centery).length()

        if distance_to_player <= self.detection_radius:
            self.is_following_player = True
        else:
            # If player is out of range, NPC might stop or revert to patrol
            # For now, let's make it stop following if it was.
            if self.is_following_player:
                self.is_following_player = False 
                # Optionally, reset to patrol behavior or a fixed spot
                # For simplicity, it will just stop moving towards player for now.

        if self.is_following_player:
            # Move towards the player
            move_vector = pygame.math.Vector2(player_rect.centerx - self.rect.centerx, 
                                              player_rect.centery - self.rect.centery)
            if move_vector.length_squared() > 0:
                move_vector = move_vector.normalize()
                self.rect.x += move_vector.x * self.speed
                self.rect.y += move_vector.y * self.speed
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
