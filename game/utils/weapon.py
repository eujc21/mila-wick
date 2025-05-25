import random
import pygame
# Import settings from the correct path
from game.core.settings import (
    WEAPON_DAMAGE_MIN, WEAPON_DAMAGE_MAX, WEAPON_FIRE_RATE_MIN, WEAPON_FIRE_RATE_MAX,
    WEAPON_PROJECTILE_SPEED_MIN, WEAPON_PROJECTILE_SPEED_MAX,
    PROJECTILE_COLOR_MIN, PROJECTILE_COLOR_MAX, DEFAULT_PROJECTILE_COLOR,
    GRENADE_DAMAGE, GRENADE_THROW_SPEED, GRENADE_COLOR, GRENADE_FUSE_TIME, # Added Grenade settings
    SCREEN_WIDTH, SCREEN_HEIGHT, GRENADE_EXPLOSION_RADIUS_FACTOR # Added Screen and Grenade Explosion Factor
)

# Predefined weapon data
WEAPON_DATA = {
    "pistol": {
        "name": "Pistol",
        "damage": 10,
        "fire_rate": 0.25,  # seconds per shot
        "projectile_speed": 12,
        "projectile_color": (128, 128, 128),  # Gray
        "type": "ranged"
    },
    "knife": {
        "name": "Knife",
        "damage": 15,
        "fire_rate": 0.5, # seconds per attack (attack speed)
        "range": 50, # pixels, effective range of the knife
        "type": "melee",
        "projectile_speed": None, # Melee weapons don\'t have projectile speed
        "projectile_color": None  # Melee weapons don\'t have projectile color
    },
    "grenade_launcher": {
        "name": "Grenade Launcher",
        "damage": GRENADE_DAMAGE, # Damage is per grenade explosion
        "fire_rate": 2.0,  # seconds per shot (slower fire rate for grenades)
        "projectile_speed": GRENADE_THROW_SPEED, # Speed of the grenade projectile
        "projectile_color": GRENADE_COLOR, # Color of the grenade projectile itself
        "type": "grenade", # New type for special handling
        "fuse_time": GRENADE_FUSE_TIME,
        "explosion_radius": (SCREEN_WIDTH + SCREEN_HEIGHT) / 2 * GRENADE_EXPLOSION_RADIUS_FACTOR
    }
    # Add more weapons here in the future, e.g.:
    # "shotgun": {
    #     "name": "Shotgun",
    #     "damage": 5, # Per pellet
    #     "fire_rate": 0.8,
    #     "projectile_speed": 10,
    #     "projectile_color": (200, 0, 0),
    #     "pellets": 5, # Custom attribute for shotgun
    #     "spread_angle": 20 # Degrees
    # }
}

class Weapon:
    def __init__(self, name, damage, fire_rate, type, projectile_speed=None, projectile_color=None, **kwargs):
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate # Can be attack speed for melee
        self.type = type
        self.projectile_speed = projectile_speed
        self.projectile_color = projectile_color
        # Store any additional weapon-specific attributes like 'range' for melee
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        attrs = [f"{key}: {getattr(self, key)}" for key in vars(self) if key != 'name']
        return f"Weapon: {self.name} ({', '.join(attrs)})"

# Removed generate_weapon() function and related lists (prefixes, nouns, suffixes)
# Removed if __name__ == '__main__' block for generate_weapon testing
