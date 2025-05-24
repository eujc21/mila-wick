\
# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
CAPTION = "My Pygame Window"

# Colors
LIGHT_GRAY = (200, 200, 200)
PINK = (255, 105, 180)
WHITE = (255, 255, 255)
BLUE = (100, 150, 255) # Player circle color if not pink
RADAR_BG_COLOR = (50, 50, 50, 150) # Semi-transparent dark gray
RADAR_LINE_COLOR = (255, 0, 0) # Red
BLACK = (0,0,0) # For projectile or other elements

# Player settings
PLAYER_RADIUS = 15
PLAYER_SPEED = 5
PLAYER_HEALTH = 100

# Room and World Settings
ROOM_WIDTH = SCREEN_WIDTH
ROOM_HEIGHT = SCREEN_HEIGHT
WORLD_ROOM_ROWS = 3
WORLD_ROOM_COLS = 3
WORLD_WIDTH = ROOM_WIDTH * WORLD_ROOM_COLS
WORLD_HEIGHT = ROOM_HEIGHT * WORLD_ROOM_ROWS

# Define more colors if needed, or use a generation scheme
ROOM_COLORS = [
    (255, 200, 200), (200, 255, 200), (200, 200, 255),
    (255, 255, 150), (255, 150, 255), (150, 255, 255),
    (220, 220, 100), (220, 100, 220), (100, 220, 220)
]
# Ensure there are enough colors for WORLD_ROOM_ROWS * WORLD_ROOM_COLS
if len(ROOM_COLORS) < WORLD_ROOM_ROWS * WORLD_ROOM_COLS:
    # Fallback: Generate random colors if not enough are predefined
    import random
    for _ in range(WORLD_ROOM_ROWS * WORLD_ROOM_COLS - len(ROOM_COLORS)):
        ROOM_COLORS.append((random.randint(100, 250), random.randint(100, 250), random.randint(100, 250)))


# Weapon settings
WEAPON_DAMAGE_MIN = 5
WEAPON_DAMAGE_MAX = 20
WEAPON_FIRE_RATE_MIN = 0.1  # Delay in seconds
WEAPON_FIRE_RATE_MAX = 0.5
WEAPON_PROJECTILE_SPEED_MIN = 8
WEAPON_PROJECTILE_SPEED_MAX = 15
PROJECTILE_COLOR_MIN = 50
PROJECTILE_COLOR_MAX = 255

# Radar Settings
RADAR_RADIUS = 40
RADAR_MARGIN = 10

# Projectile Settings
PROJECTILE_WIDTH = 10
PROJECTILE_HEIGHT = 4
DEFAULT_PROJECTILE_COLOR = (255, 0, 0) # Red, as requested

# Melee Attack Visuals
MELEE_VISUAL_DURATION = 100  # milliseconds
MELEE_ATTACK_COLOR = (255, 0, 0, 150) # Red, slightly transparent for alpha
