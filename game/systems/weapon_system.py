# In game/systems/weapon_system.py

# (Ensure these imports are correct based on current file locations)
import pygame
from projectile import Projectile # Will be game.entities.projectile.Projectile later
from grenade import Grenade     # Will be game.entities.grenade.Grenade later
# from game.core.settings import MELEE_ATTACK_COLOR # Example, if needed directly

class WeaponSystem:
    def __init__(self, entity_manager, effect_manager, combat_manager):
        self.entity_manager = entity_manager
        self.effect_manager = effect_manager
        self.combat_manager = combat_manager
        self.last_use_times = {}

    def _get_melee_attack_rect(self, wielder_entity):
        # ... (implementation from previous step, ensure it's correct) ...
        # (Copied from previous for context, ensure it's present and correct in actual file)
        if not hasattr(wielder_entity, 'weapon') or            not hasattr(wielder_entity.weapon, 'range') or            wielder_entity.weapon.type != "melee":
            return None
        attack_range = wielder_entity.weapon.range
        direction = getattr(wielder_entity, 'direction', pygame.math.Vector2(0,1))
        # Player has 'radius', NPC might not. Default to half width.
        radius = getattr(wielder_entity, 'radius', wielder_entity.rect.width / 2) 
        norm_direction = direction.normalize() if direction.length_squared() > 0 else pygame.math.Vector2(0,1)
        effective_center_x = wielder_entity.rect.centerx + norm_direction.x * (radius + attack_range / 2.0)
        effective_center_y = wielder_entity.rect.centery + norm_direction.y * (radius + attack_range / 2.0)
        perpendicular_width = radius * 1.5 
        if abs(norm_direction.x) > abs(norm_direction.y): 
            rect_width = attack_range
            rect_height = perpendicular_width
        else: 
            rect_width = perpendicular_width
            rect_height = attack_range
        attack_rect = pygame.Rect(0, 0, rect_width, rect_height)
        attack_rect.center = (effective_center_x, effective_center_y)
        return attack_rect


    def use_weapon(self, wielder_entity, target_info=None): # target_info for NPC->Player attacks primarily
        weapon = wielder_entity.weapon
        if not weapon:
            return False

        current_time = pygame.time.get_ticks()
        cooldown_key = (id(wielder_entity), weapon.type)
        last_use = self.last_use_times.get(cooldown_key, 0)
        
        # Ensure fire_rate is a positive number to avoid division by zero or negative cooldowns
        fire_rate_seconds = getattr(weapon, 'fire_rate', 1.0) # Default to 1s if not set
        if fire_rate_seconds <= 0:
            fire_rate_seconds = 0.001 # Prevent zero or negative cooldowns

        if current_time - last_use < fire_rate_seconds * 1000:
            return False # Still in cooldown

        action_performed = False
        if weapon.type == "ranged" or weapon.type == "grenade":
            # Common logic for projectile direction and spawn point
            # Assumes wielder_entity has 'direction', 'rect', and 'radius'
            direction = getattr(wielder_entity, 'direction', pygame.math.Vector2(0,1))
            fire_direction = direction.normalize() if direction.length_squared() > 0 else pygame.math.Vector2(0,1)
            
            radius = getattr(wielder_entity, 'radius', wielder_entity.rect.width / 2) # Player has radius
            spawn_offset_distance = radius + 5 
            spawn_offset = fire_direction * spawn_offset_distance
            
            proj_x = wielder_entity.rect.centerx + spawn_offset.x
            proj_y = wielder_entity.rect.centery + spawn_offset.y

            if weapon.type == "ranged":
                projectile = Projectile(proj_x, proj_y, fire_direction, weapon)
                self.entity_manager.add_entity(projectile, "projectile")
                action_performed = True
            elif weapon.type == "grenade":
                # Grenade needs npcs_group for its explode method's targeting logic
                # and owner for kill attribution (though kill attribution is moving to events)
                npcs_group = self.entity_manager.npcs # Grenade's internal targeting uses this
                grenade = Grenade(proj_x, proj_y, fire_direction, weapon, 
                                  npcs_group, # Pass the group of NPCs for grenade's own targeting
                                  wielder_entity) # Owner
                self.entity_manager.add_entity(grenade, "projectile")
                action_performed = True
        
        elif weapon.type == "melee":
            attack_rect = self._get_melee_attack_rect(wielder_entity)
            if attack_rect:
                # Create visual effect
                # The direction for the visual should be the wielder's facing direction
                wielder_direction = getattr(wielder_entity, 'direction', pygame.math.Vector2(0,1))
                self.effect_manager.create_attack_visual(
                    center_pos=attack_rect.center, # Or a point related to wielder + direction
                    width=attack_rect.width,     # Or weapon.range
                    height=attack_rect.height,   # Or a fixed thickness
                    direction_vector=wielder_direction
                )
                
                # Handle damage based on wielder type
                # This assumes Player and NPC are the primary wielders for now.
                if wielder_entity.__class__.__name__ == 'Player': # A more robust check is isinstance
                    self.entity_manager.handle_player_melee_on_npcs(attack_rect, weapon.damage, wielder_entity)
                elif wielder_entity.__class__.__name__ == 'NPC':
                    # NPC melee: target_info is expected to be the player_sprite
                    player_to_attack = target_info 
                    if player_to_attack and attack_rect.colliderect(player_to_attack.rect):
                        if player_to_attack.alive:
                             self.combat_manager.inflict_damage_on_player(player_to_attack, weapon.damage, wielder_entity)
                action_performed = True

        if action_performed:
            self.last_use_times[cooldown_key] = current_time
            print(f"WeaponSystem: {wielder_entity.__class__.__name__} (ID: {id(wielder_entity)}) successfully used {weapon.name}")
            return True
        
        return False # No action performed (e.g. wrong weapon type if not caught above, or other failure)
