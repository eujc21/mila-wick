# Dependency Map

This document tracks the major class and module interdependencies in the Mila Wick project.

## Core Gameplay (`main.py`)

-   **`Game` Class:**
    -   Initializes Pygame, screen, clock.
    -   Manages game loop, event handling, updates, and rendering.
    -   **Depends on:**
        -   `pygame`
        -   `settings.py` (for screen dimensions, FPS, colors, world/room config, UI elements)
        -   `Player` (creates and manages player instance)
        -   `Room` (creates and manages room instances)
        -   `NPC` (creates and manages NPC instances)
        -   `Projectile` (indirectly via `Player.shoot()`)
        -   `Grenade` (indirectly via `Player.shoot()` when grenade launcher is equipped)
        -   `ExplosionEffect` (indirectly via `Grenade.explode()`)
    -   **Key Methods:**
        -   `__init__()`: Sets up game, player, rooms, NPCs, camera, UI elements.
        -   `run()`: Main game loop. Handles events:
            -   Player movement (delegated to `Player.update()`).
            -   Player shooting (`Player.shoot()`).
                -   Passes `projectiles` (Sprite Group), `all_sprites` (Sprite Group), and `npcs` (Sprite Group) to `Player.shoot()`.
            -   Player melee attack (`Player.melee_attack()`).
                -   Checks for collision with `npcs`.
            -   Weapon switching (`Player.equip_weapon()` for "pistol", "knife", "grenade_launcher").
            -   Updates all sprites in `all_sprites`.
            -   Handles projectile-NPC collisions (calls `npc.take_damage()`, `projectile.kill()`).
        -   `update_camera()`: Adjusts camera based on player position.
        -   `draw_radar()`, `draw_status_bar()`, `draw_minimap()`: UI rendering.

## Player (`player.py`)

-   **`Player(pygame.sprite.Sprite)` Class:**
    -   Represents the player character.
    -   **Depends on:**
        -   `pygame`
        -   `settings.py` (for player stats, colors, world dimensions)
        -   `Weapon` (holds current weapon instance)
        -   `WEAPON_DATA` (from `weapon.py`, for equipping weapons)
        -   `Projectile` (instantiated in `shoot()` for ranged weapons)
        -   `Grenade` (instantiated in `shoot()` for grenade launcher)
    -   **Key Attributes:**
        -   `weapon: Weapon`
    -   **Key Methods:**
        -   `__init__()`: Initializes player stats, image, position, initial weapon.
        -   `update()`: Handles movement input, updates position, clamps to world boundaries, redraws image if direction changes.
        -   `shoot(projectiles_group, all_sprites_group, npcs_group)`:
            -   Handles firing logic based on `self.weapon.type`.
            -   If `type == "ranged"`, creates `Projectile` instance.
            -   If `type == "grenade"`, creates `Grenade` instance, passing `all_sprites_group` and `npcs_group` to it.
            -   Adds projectiles/grenades to `projectiles_group` and `all_sprites_group`.
        -   `melee_attack()`: Performs melee attack, returns attack rectangle.
        -   `equip_weapon(weapon_key)`: Switches player's weapon using `WEAPON_DATA`.
        -   `get_melee_attack_rect()`: Calculates melee attack area.

## Weapons (`weapon.py`)

-   **`Weapon` Class:**
    -   Represents a weapon's attributes.
    -   **Depends on:**
        -   `settings.py` (for default grenade properties if not in `WEAPON_DATA`)
    -   **Key Attributes:**
        -   `name`, `damage`, `fire_rate`, `type` (`"ranged"`, `"melee"`, `"grenade"`)
        -   `projectile_speed`, `projectile_color`
        -   Other dynamic attributes via `**kwargs` (e.g., `range` for melee, `fuse_time`, `explosion_radius` for grenade launcher).
-   **`WEAPON_DATA` Dictionary:**
    -   Defines attributes for all available weapons (e.g., "pistol", "knife", "grenade_launcher").
    -   "grenade_launcher" entry includes `type: "grenade"`, `fuse_time`, `explosion_radius`.
    -   **Used by:** `Player.equip_weapon()`.

## Projectiles

### `projectile.py`

-   **`Projectile(pygame.sprite.Sprite)` Class:**
    -   Base class for projectiles.
    -   **Depends on:**
        -   `pygame`
        -   `settings.py` (for default projectile size/color if not overridden)
        -   `Weapon` (instance passed to constructor to get stats like speed, damage, color)
    -   **Key Methods:**
        -   `__init__(x, y, direction_vector, weapon_stats)`
        -   `update()`: Moves projectile, kills if off-screen.

### `grenade.py`

-   **`Grenade(Projectile)` Class:**
    -   Specialized projectile that explodes.
    -   **Depends on:**
        -   `pygame`
        -   `Projectile` (base class)
        -   `settings.py` (for default grenade stats, explosion color)
        -   `ExplosionEffect` (created in `explode()`)
        -   `NPC` (iterates through `npcs_group` in `explode()` to apply damage)
    -   **Key Attributes (from `weapon_stats` or defaults):**
        -   `fuse_time`, `explosion_radius`, `grenade_damage`
    -   **Key Methods:**
        -   `__init__(x, y, direction_vector, weapon_stats, all_sprites_group, npcs_group)`:
            -   Sets grenade-specific properties from `weapon_stats`.
            -   Stores `all_sprites_group` (to add `ExplosionEffect`) and `npcs_group` (to damage NPCs).
        -   `update()`: Manages fuse timer; calls `explode()` when timer ends.
        -   `explode()`:
            -   Creates `ExplosionEffect`.
            -   Checks for NPCs within `explosion_radius` and calls `npc.take_damage()`.
-   **`ExplosionEffect(pygame.sprite.Sprite)` Class:**
    -   Visual effect for grenade explosion.
    -   **Depends on:**
        -   `pygame`
    -   **Key Methods:**
        -   `__init__(center, radius, color, duration)`
        -   `update()`: Kills sprite after `duration`.

## NPCs (`npc.py`)

-   **`NPC(pygame.sprite.Sprite)` Class:**
    -   Represents Non-Player Characters.
    -   **Depends on:**
        -   `pygame`
        -   `settings.py` (for NPC stats, colors, behavior parameters)
    -   **Key Methods:**
        -   `take_damage(amount)`: Reduces NPC health.
        -   `update(player_rect)`: Handles movement (patrolling, following player), updates image.

## Settings (`settings.py`)

-   Contains all game constants:
    -   Screen, FPS, colors.
    -   Player, NPC, projectile, **grenade** stats (speed, damage, fuse time, explosion radius, colors).
    -   Weapon defaults (though many are now in `WEAPON_DATA`).
    -   World, room, UI (radar, minimap) dimensions and colors.

## Previous `DEPENDENCY_MAP.md` content (for reference, to be merged/updated)

### Implemented (from previous state):
-   ✅ Collision detection between projectiles and NPCs (`Game.run()`, `pygame.sprite.spritecollide()`).
-   ✅ Damage application from projectile collisions (`Game.run()` calls `npc.take_damage()`).
-   ✅ Damage application from melee attacks (`Game.run()` checks `attack_rect.colliderect(npc.rect)` and calls `npc.take_damage()`).
-   ✅ Projectile destruction on hit (`projectile.kill()` in `Game.run()`).

### Current State of Damage & Collision:
-   **Projectile Damage:**
    -   `Game.run()`: Iterates `self.projectiles`. `pygame.sprite.spritecollide(projectile, self.npcs, False)` detects hits.
    -   If hit, `npc.take_damage(projectile.damage)` is called.
    -   `projectile.kill()` is called.
-   **Melee Damage:**
    -   `Game.run()`: On spacebar press with melee weapon:
        -   `attack_rect = self.player.melee_attack()`.
        -   Iterates `self.npcs`. If `attack_rect.colliderect(npc.rect)`, then `npc.take_damage(self.player.weapon.damage)`.
-   **Grenade Damage:**
    -   `Grenade.explode()`: Iterates `self.npcs` (passed during `Grenade` creation).
    -   If NPC is within `self.explosion_radius`, `npc.take_damage(self.grenade_damage)`.

This map should be updated as new features are added or existing ones are modified.