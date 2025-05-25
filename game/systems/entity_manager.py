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

    def handle_collisions(self, effect_manager): # effect_manager added to signature
        # Projectile-NPC collisions
        # Need to import Grenade if type checking, ensure path is correct based on current file structure
        # For now, let's assume grenade.py is still in root, so use 'from grenade import Grenade'
        # This import will need to be updated when grenade.py moves.
        try:
            from grenade import Grenade # Temporary import, adjust path as needed
        except ImportError:
            # Fallback if grenade.py has moved to game/entities/grenade.py
            from game.entities.grenade import Grenade


        for projectile in list(self.projectiles): # Iterate over a copy for safe removal
            # Check collision between this projectile and the group of NPCs
            hit_npcs = pygame.sprite.spritecollide(projectile, self.npcs, False) # False: don't kill npcs automatically

            if hit_npcs:
                if isinstance(projectile, Grenade):
                    if not projectile.detonated:
                        projectile.explode(effect_manager) # Pass effect_manager
                    # Grenade.kill() is called by its own explode or update logic, or it might be killed by range in Projectile.update
                    # If it was a contact grenade that explodes on first hit, ensure it's killed.
                    # For now, assume fuse or range handles its removal after explosion.
                    # projectile.kill() # Ensure grenade is removed after processing if it should be. 
                    # This might be redundant if explode() or update() handles it.
                    # For now, let's assume grenade's own logic or its Projectile parent class update handles removal.
                    print(f"EntityManager: Grenade event processed.")
                else: # For regular projectiles
                    for npc in hit_npcs: # Should typically be one NPC for a non-exploding projectile
                        npc.take_damage(projectile.damage)
                        projectile.kill()  # Remove projectile after hit
                        print(f"EntityManager: Projectile hit NPC for {projectile.damage} damage!")
                        break # Projectile hits one NPC and is destroyed

        def handle_player_melee_on_npcs(self, attack_rect, weapon_damage, attacking_player):
            if not attack_rect:
                return

            for npc in self.npcs:
                # Ensure the NPC is not the attacker itself, though NPCs are typically not players.
                # This is more relevant if this method were generalized for any entity attacking NPCs.
                if npc is attacking_player: 
                    continue

                if attack_rect.colliderect(npc.rect):
                    if npc.alive: # Only damage alive NPCs
                        npc.take_damage(weapon_damage)
                        print(f"EntityManager: Melee attack by {attacking_player.__class__.__name__} hit NPC for {weapon_damage} damage!")
                        # Potentially, this method could return a list of hit NPCs if needed elsewhere.
