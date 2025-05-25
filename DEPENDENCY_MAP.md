# Dependency Map

This document tracks the major class and module interdependencies in the Mila Wick project.

## Core Gameplay (`main.py`)

-   **`Game` Class:**
    -   Initializes Pygame, screen, clock.
    -   Manages game loop, event handling, updates, and rendering.
    -   **Depends on:**
        -   `pygame`
        -   `settings.py` (for screen dimensions, FPS, colors, world/room config, UI elements, wave settings)
        -   `Player` (creates and manages player instance)
        -   `Room` (creates and manages room instances)
        -   `NPC` (manages NPC group, NPCs created by `WaveManager`)
        -   `Projectile` (indirectly via `Player.shoot()`)
        -   `Grenade` (indirectly via `Player.shoot()` when grenade launcher is equipped)
        -   `ExplosionEffect` (indirectly via `Grenade.explode()`)
        -   `WaveManager` (creates and manages wave manager instance)
    -   **Key Methods:**
        -   `__init__()`: Sets up game, player, rooms, camera, UI elements, `WaveManager`.
        -   `run()`: Main game loop. Handles events:
            -   Player movement (delegated to `Player.update()`).
            -   Player shooting (`Player.shoot()`).
                -   Passes `projectiles` (Sprite Group), `all_sprites` (Sprite Group), and `npcs` (Sprite Group) to `Player.shoot()`.
            -   Player melee attack (`Player.melee_attack()`).
                -   Checks for collision with `npcs`.
            -   Weapon switching (`Player.equip_weapon()` for "pistol", "knife", "grenade_launcher").
            -   Updates all sprites in `all_sprites`.
            -   Updates `WaveManager` (`wave_manager.update()`).
            -   Handles projectile-NPC collisions (calls `npc.take_damage()`, `projectile.kill()`).
            -   Handles grenade-NPC collisions (calls `grenade.explode()`).
        -   `update_camera()`: Adjusts camera based on player position.
        -   `draw_radar()`, `draw_status_bar()`, `draw_minimap()`: UI rendering.
            - `draw_status_bar()` now displays kills (`player.kills`) and wave info (`wave_manager.get_wave_status_text()`).

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
        -   `kills: int` (tracks number of NPCs killed by the player)
    -   **Key Methods:**
        -   `__init__()`: Initializes player stats, image, position, initial weapon, `kills` count.
        -   `update()`: Handles movement input, updates position, clamps to world boundaries, redraws image if direction changes.
        -   `shoot(projectiles_group, all_sprites_group, npcs_group)`:
            -   Handles firing logic based on `self.weapon.type`.
            -   If `type == "ranged"`, creates `Projectile` instance.
            -   If `type == "grenade"`, creates `Grenade` instance, passing `all_sprites_group`, `npcs_group`, and `self` (player instance for kill tracking) to it.
            -   Adds projectiles/grenades to `projectiles_group` and `all_sprites_group`.
        -   `melee_attack()`: Performs melee attack, returns attack rectangle.
        -   `equip_weapon(weapon_key)`: Switches player's weapon using `WEAPON_DATA`.
        -   `get_melee_attack_rect()`: Calculates melee attack area.
        -   `increment_kills()`: Increments the player's kill count.

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
        -   `settings.py` (for default projectile size/color, `PROJECTILE_MAX_RANGE`)
        -   `Weapon` (instance passed to constructor to get stats like speed, damage, color)
    -   **Key Methods:**
        -   `__init__(x, y, direction_vector, weapon_stats)`: Stores `start_x`, `start_y` for range calculation.
        -   `update()`: Moves projectile, kills if off-screen or `PROJECTILE_MAX_RANGE` is exceeded.

### `grenade.py`

-   **`Grenade(Projectile)` Class:**
    -   Specialized projectile that explodes.
    -   **Depends on:**
        -   `pygame`
        -   `Projectile` (base class)
        -   `settings.py` (for default grenade stats, explosion color)
        -   `ExplosionEffect` (created in `explode()`)
        -   `NPC` (iterates through `npcs_group` in `explode()` to apply damage)
        -   `Player` (stores `owner` instance, passed from `Player.shoot()`)
    -   **Key Attributes (from `weapon_stats` or defaults):**
        -   `fuse_time`, `explosion_radius`, `grenade_damage`
        -   `owner: Player` (used to attribute kills, though `NPC.take_damage` handles incrementing)
    -   **Key Methods:**
        -   `__init__(x, y, direction_vector, weapon_stats, all_sprites_group, npcs_group, owner)`:
            -   Sets grenade-specific properties from `weapon_stats`.
            -   Stores `owner`.
        -   `update()`: Manages fuse timer; calls `explode()` when fuse ends.
        -   `explode()`: Creates `ExplosionEffect`, damages NPCs in radius (calls `npc.take_damage()`), kills self.

## NPCs (`npc.py`)

-   **`NPC(pygame.sprite.Sprite)` Class:**
    -   Represents a non-player character.
    -   **Depends on:**
        -   `pygame`
        -   `settings.py` (for NPC stats, colors, movement behavior)
        -   `Player` (optional `player_instance` for kill tracking)
    -   **Key Attributes:**
        -   `health`, `speed`, `damage`
        -   `player_instance: Player` (optional, for kill tracking)
    -   **Key Methods:**
        -   `__init__(x, y, player_instance=None)`: Initializes NPC, optionally stores `player_instance`.
        -   `update(player_rect)`: Handles movement (patrolling or following player).
        -   `take_damage(amount)`: Reduces health. If health <= 0, kills NPC and calls `player_instance.increment_kills()` if `player_instance` exists.

## Effects (`grenade.py` - might be moved later)

-   **`ExplosionEffect(pygame.sprite.Sprite)` Class:**
    -   Visual effect for grenade explosion.
    -   **Depends on:**
        -   `pygame`
        -   `settings.py` (for explosion duration, color)
    -   **Key Methods:**
        -   `__init__(center_x, center_y, radius, color, duration)`
        -   `update()`: Manages visual effect lifetime.

## World & Rooms (`room.py`)

-   **`Room` Class:**
    -   Represents a single room in the game world.
    -   **Depends on:**
        -   `pygame`
        -   `settings.py` (for room dimensions)
    -   **Key Methods:**
        -   `__init__(grid_x, grid_y, color)`
        -   `draw(surface, camera_x, camera_y)`: Draws room relative to camera.

## Wave Management (`wave_manager.py`)

-   **`WaveManager` Class:**
    -   Manages NPC spawning in waves.
    -   **Depends on:**
        -   `pygame` (for timing)
        -   `settings.py` (for `WAVE_REST_TIME`, world dimensions for spawning)
        -   `NPC` (instantiates NPCs)
        -   `Player` (passed as `player_reference` to `NPC` for kill tracking)
    -   **Key Attributes:**
        -   `all_sprites_group`, `npcs_group` (references to sprite groups in `Game`)
        -   `player_reference: Player`
        -   `world_width`, `world_height`
    -   **Key Methods:**
        -   `__init__(all_sprites_group, npcs_group, player_reference, world_width, world_height)`
        -   `update()`: Manages wave timing (active vs. rest), starts new waves.
        -   `start_next_wave()`: Increments wave number, calculates NPC count (Fibonacci), calls `spawn_npcs()`.