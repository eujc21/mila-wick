import pygame

class EntityManager:
    def __init__(self):
        self.entities = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        # It might also be useful to have a group for grenades if they need special handling
        # apart from generic projectiles, or if other entity types are introduced.
        # For now, the provided structure is fine.

    def add_entity(self, entity, entity_type_str: str):
        '''
        Adds an entity to the main 'entities' group and its type-specific group.
        entity_type_str should be one of 'player', 'npc', 'projectile'.
        '''
        self.entities.add(entity)
        
        type_group_name = f"{entity_type_str.lower()}s" # e.g., "players", "npcs"
        if hasattr(self, type_group_name):
            getattr(self, type_group_name).add(entity)
        else:
            print(f"Warning: EntityManager has no group named '{type_group_name}' for entity type '{entity_type_str}'")

    def update(self, dt): # dt for delta time
        # This method will call the update method of all managed entities.
        # The 'dt' parameter should be passed to each entity's update method.
        # For example: for entity in self.entities: entity.update(dt)
        # However, the base Entity.update(dt) currently does 'pass'.
        # Player.update() and NPC.update(player_rect, player_object) have different signatures.
        # Projectile.update() also doesn't take dt.
        # This needs to be harmonized later.
        # For now, let's call update on entities that match the base class or Projectile signature.
        # More complex entities (Player, NPC) will be updated by other systems or directly by the game loop for now.
        
        # Tentative update logic - this will evolve:
        for entity in self.entities:
            if hasattr(entity, 'update'):
                # Try to call update with dt if the entity's update method accepts it.
                # This is a bit of a simplification; proper component-based systems would handle this differently.
                # For now, we'll assume entities that need dt will have update(self, dt).
                # Others (like Player, NPC with custom update args) won't be updated here yet.
                # This will be refined as other systems (MovementSystem, AISystem) are introduced.
                try:
                    # This is a bit hacky. A better way would be to standardize update signatures
                    # or have systems manage updates for specific entity types/components.
                    # For now, only call update if it seems like the simple version.
                    if entity.__class__.__name__ in ["Projectile", "Grenade", "ExplosionEffect", "AttackVisual"] or isinstance(entity, pygame.sprite.Sprite) and not hasattr(entity, 'player_rect'): # Avoid calling complex updates
                         entity.update() # Projectile, ExplosionEffect, AttackVisual use update()
                    # else if it takes dt (like base Entity, though it's a pass)
                    # elif 'dt' in entity.update.__code__.co_varnames:
                    #    entity.update(dt)
                except TypeError as e:
                    # print(f"Note: Could not call update() on {entity} with dt: {e}")
                    # Fallback for entities that don't take dt (like current Projectile)
                    # entity.update() # This was the original attempt.
                    pass # Let specific systems handle their updates for now.
        
        # The main responsibility of EntityManager.update() will likely be to call entity.update(dt)
        # once entity update signatures are more harmonized or specific systems take over.
        # For now, it can be kept simple or even mostly empty if other systems will handle updates.

    def draw(self, surface, camera=None):
        # This method will draw all managed entities.
        # If a camera is used, entities should be drawn offset by the camera position.
        if camera:
            for entity in self.entities:
                if hasattr(entity, 'rect') and hasattr(entity, 'image'):
                    surface.blit(entity.image, camera.apply(entity.rect))
        else:
            for entity in self.entities:
                 if hasattr(entity, 'rect') and hasattr(entity, 'image'):
                    surface.blit(entity.image, entity.rect)
        # Pygame's Group.draw(surface) is often more efficient if all entities are in self.entities
        # and have 'image' and 'rect'.
        # self.entities.draw(surface) # This is simpler if no camera offset is needed here.
        # If camera offset is needed for all, Group.draw doesn't support it directly,
        # so manual iteration is common.

    def handle_collisions(self):
        # Centralized collision detection logic will go here.
        # This will be implemented in a later step.
        # Example: pygame.sprite.groupcollide(self.projectiles, self.npcs, True, True)
        pass
