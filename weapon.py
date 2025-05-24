\
import random
import pygame # Keep for pygame.math.Vector2 if needed for more complex weapons later
from settings import (
    WEAPON_DAMAGE_MIN, WEAPON_DAMAGE_MAX,
    WEAPON_FIRE_RATE_MIN, WEAPON_FIRE_RATE_MAX,
    WEAPON_PROJECTILE_SPEED_MIN, WEAPON_PROJECTILE_SPEED_MAX,
    PROJECTILE_COLOR_MIN, PROJECTILE_COLOR_MAX
)

prefixes = ["Sharp", "Pointy", "Mighty", "Mega", "Scribble"]
nouns = ["Pencil", "Crayon", "Fork", "Spoon", "Block"]
suffixes = ["of Doom", "of Annoyance", "of Justice", "of Naptime"]

class Weapon:
    def __init__(self, name, damage, fire_rate, projectile_speed, projectile_color):
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate  # Delay in seconds between shots
        self.projectile_speed = projectile_speed
        self.projectile_color = projectile_color

    def __str__(self):
        return f"Weapon: {self.name}, DMG: {self.damage}, Rate: {self.fire_rate:.2f}, ProjSpeed: {self.projectile_speed}, Color: {self.projectile_color}"

def generate_weapon():
    name = f"{random.choice(prefixes)} {random.choice(nouns)} {random.choice(suffixes)}"
    damage = random.randint(WEAPON_DAMAGE_MIN, WEAPON_DAMAGE_MAX)
    fire_rate = random.uniform(WEAPON_FIRE_RATE_MIN, WEAPON_FIRE_RATE_MAX)
    projectile_speed = random.randint(WEAPON_PROJECTILE_SPEED_MIN, WEAPON_PROJECTILE_SPEED_MAX)
    projectile_color = (
        random.randint(PROJECTILE_COLOR_MIN, PROJECTILE_COLOR_MAX),
        random.randint(PROJECTILE_COLOR_MIN, PROJECTILE_COLOR_MAX),
        random.randint(PROJECTILE_COLOR_MIN, PROJECTILE_COLOR_MAX)
    )
    return Weapon(name, damage, fire_rate, projectile_speed, projectile_color)

if __name__ == '__main__':
    # For testing weapon generation
    for _ in range(5):
        print(generate_weapon())
