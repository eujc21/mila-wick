\
# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
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

# Leaderboard UI Colors
UI_WHITE = (255, 255, 255)
UI_BLACK = (0, 0, 0)
UI_GRAY = (128, 128, 128)
UI_LIGHT_BLUE = (173, 216, 230)
UI_INPUT_BOX_COLOR = (200, 200, 200)
UI_INPUT_TEXT_COLOR = UI_BLACK
UI_PROMPT_COLOR = UI_WHITE
UI_SCORE_TEXT_COLOR = UI_WHITE
UI_CURSOR_COLOR = UI_BLACK
UI_LEADERBOARD_OVERLAY_COLOR = (0, 0, 0, 180) # Dark semi-transparent

# UI Font Settings
UI_FONT_NAME = "arial"  # Default font name
UI_FONT_SIZE_TITLE = 36
UI_FONT_SIZE_SCORE = 28
UI_FONT_SIZE_INPUT = 24

# Consolidating UI Colors into a dictionary for easier management in tests or UI components
UI_COLORS = {
    "background": (30, 30, 30, 200),  # Dark semi-transparent
    "text": UI_WHITE,
    "highlight": UI_LIGHT_BLUE,
    "input_background": UI_INPUT_BOX_COLOR,
    "input_text": UI_INPUT_TEXT_COLOR,
    "border": UI_GRAY,
    "title": UI_WHITE,
    "score": UI_WHITE,
    "prompt": UI_PROMPT_COLOR,
    "cursor": UI_CURSOR_COLOR,
    "overlay": UI_LEADERBOARD_OVERLAY_COLOR
}

# Player settings
PLAYER_RADIUS = 15
PLAYER_SPEED = 4
PLAYER_HEALTH = 100
PLAYER_START_X = SCREEN_WIDTH // 2 # Added PLAYER_START_X
PLAYER_START_Y = SCREEN_HEIGHT // 2 # Added PLAYER_START_Y

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
PROJECTILE_HEIGHT = 5
PROJECTILE_MAX_RANGE = 300 # Default maximum distance a projectile can travel
DEFAULT_PROJECTILE_COLOR = (255, 0, 0) # Red, as requested

# Melee Attack Visuals
MELEE_VISUAL_DURATION = 100  # milliseconds
MELEE_ATTACK_COLOR = (255, 0, 0, 150) # Red, slightly transparent for alpha

# NPC Settings
NPC_WIDTH = 30
NPC_HEIGHT = 30
NPC_SPEED = 2
NPC_COLOR = (0, 0, 255) # Blue
NPC_MOVEMENT_RANGE = 200 # How far an NPC can move from its starting point
NPC_HEALTH = 50
NPC_DETECTION_RADIUS = 150 # How close the player needs to be for the NPC to follow
NPC_CHASE_AREA_MULTIPLIER = 10 # Multiplier for detection radius when chasing
NPC_PATROL_COLOR_HORIZONTAL = (255, 255, 0, 100) # Yellow, semi-transparent
NPC_PATROL_COLOR_VERTICAL = (0, 255, 255, 100) # Cyan, semi-transparent
NPC_MELEE_COOLDOWN = 1000 # Milliseconds (1 second) between NPC attacks - This can be a default if weapon has no fire_rate

# Item Settings
ITEM_SIZE = (20, 20) # Default size for items
HEALTH_PACK_COLOR = (0, 255, 0) # Green for health pack
HEALTH_PACK_VALUE = 25 # How much health a pack restores
HEALTH_PACK_DROP_CHANCE = 0.25 # Chance for an NPC to drop a health pack (e.g., 0.1 for 10%)

# Grenade Settings
GRENADE_COLOR = (255, 165, 0) # Orange
GRENADE_EXPLOSION_COLOR = (255, 69, 0, 180) # Orangey-red, semi-transparent
GRENADE_FUSE_TIME = 3000 # Milliseconds (3 seconds)
GRENADE_THROW_SPEED = 7 # Speed at which grenade is thrown
GRENADE_MAX_THROW_DISTANCE_FACTOR = 0.25 # Factor of SCREEN_WIDTH
GRENADE_EXPLOSION_RADIUS_FACTOR = 0.05 # Factor of average screen dimension ( (SCREEN_WIDTH + SCREEN_HEIGHT) / 2 )
GRENADE_DAMAGE = 75
MIN_WAVE_FOR_GRENADE = 3 # Example: Grenades available from wave 3

# Wave Manager Settings
WAVE_REST_TIME = 3000 # Milliseconds (3 seconds)

# Minimap Settings
MINIMAP_WIDTH = 150
MINIMAP_HEIGHT = 100
MINIMAP_MARGIN = 10
MINIMAP_BG_COLOR = (30, 30, 30, 200)  # Dark semi-transparent
MINIMAP_ROOM_COLOR = (100, 100, 100) # Gray for rooms
MINIMAP_PLAYER_COLOR = (255, 0, 0)   # Red for player
MINIMAP_BORDER_COLOR = (150, 150, 150) # Light gray for border
MINIMAP_HEALTH_PACK_COLOR = (0, 255, 0, 200) # Green, semi-transparent for minimap
