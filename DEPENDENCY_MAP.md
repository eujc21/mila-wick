# Project Dependency Map

This document outlines the dependencies between different modules and classes in the Mila Wick project.

## Core Modules

*   **`game.core.settings`**: Defines global constants and settings for the game. 
    *   Referenced by: `game.world.room`, `main`, `item`, `game.utils.weapon`, `game.ui.leaderboard_sprite`, `game.entities.projectile`, `game.entities.npc`, `game.core.game`, `tests.test_player`, `tests.test_leaderboard_sprite` (and potentially others after import fixes).
*   **`game.core.game`**: Main game class, orchestrates game loop, events, and updates.
    *   Dependencies: `pygame`, `game.core.settings`, `game.entities.player`, `game.world.room`, `game.entities.projectile`, `game.entities.npc`, `game.entities.grenade`, `game.systems.wave_manager`, `game.ui.leaderboard`, `game.core.camera`, `game.systems.entity_manager`, `game.systems.combat_system`, `game.core.event_manager`, `item`
*   **`game.core.entity`**: Base class for all game entities.
    *   Referenced by: `game.entities.player`, `game.entities.projectile`, `game.entities.npc`, `game.entities.grenade`, `item`
*   **`game.core.camera`**: Handles camera movement and positioning.
    *   Dependencies: `pygame`
*   **`game.core.event_manager`**: Manages custom game events.
    *   Dependencies: `pygame`

## Entities

*   **`game.entities.player`**: Represents the player character.
    *   Dependencies: `pygame`, `game.core.entity`, `game.core.settings`, `game.utils.weapon`, `game.entities.projectile`, `game.entities.grenade`
*   **`game.entities.npc`**: Represents non-player characters (enemies).
    *   Dependencies: `pygame`, `game.core.entity`, `game.core.settings`, `game.utils.weapon`
*   **`game.entities.projectile`**: Represents projectiles fired by weapons.
    *   Dependencies: `pygame`, `game.core.entity`, `game.core.settings`
*   **`game.entities.grenade`**: Represents grenades.
    *   Dependencies: `pygame`, `game.entities.projectile`, `game.core.settings`
*   **`item`**: Represents items that can be picked up.
    *   Dependencies: `pygame`, `game.core.entity`, `game.core.settings`

## Game Systems

*   **`game.systems.combat_system`**: Manages combat interactions.
    *   Dependencies: `pygame`, `game.core.settings`, `game.entities.projectile`
*   **`game.systems.entity_manager`**: Manages all game entities.
    *   Dependencies: `pygame`
*   **`game.systems.wave_manager`**: Manages waves of enemies.
    *   Dependencies: `pygame`, `game.entities.npc`, `game.core.settings`
*   **`game.systems.weapon_system`**: Manages weapon mechanics.
    *   Dependencies: `pygame`, `game.entities.projectile`, `game.entities.grenade`

## UI

*   **`game.ui.leaderboard`**: Manages the leaderboard display and logic.
    *   Dependencies: `pygame`, `sqlite3`, `game.core.settings`
*   **`game.ui.leaderboard_sprite`**: Sprite for leaderboard entries.
    *   Dependencies: `pygame`, `game.core.settings`
*   **`game.ui.ui_manager`**: Manages UI elements.
    *   Dependencies: `pygame`

## Utilities

*   **`game.utils.effects`**: Handles visual effects.
    *   Dependencies: `pygame`
*   **`game.utils.weapon`**: Defines weapon properties and behavior.
    *   Dependencies: `pygame`, `game.core.settings`

## World

*   **`game.world.room`**: Defines individual rooms in the game world.
    *   Dependencies: `pygame`, `game.core.settings`

## Main & Tests

*   **`main.py`**: Entry point of the application.
    *   Dependencies: `game.core.game`
*   **`tests.*`**: Pytest files for unit testing.
    *   Dependencies: Vary, but often include `pygame` and relevant game modules.

This map will be updated as the codebase evolves.