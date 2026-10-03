"""Spring Crack — platformer settings."""

# Window
WIDTH = 800
HEIGHT = 640
FPS = 60
TITLE = "Spring Crack"

# Physics (smooth feel)
GRAVITY = 0.52
MOVE_SPEED = 5.6
ACCEL = 0.85
FRICTION = 0.78
AIR_CONTROL = 0.65
JUMP_VELOCITY = -12.0
MAX_FALL = 13
COYOTE_FRAMES = 8
NEXT_LEVEL_DELAY = 90  # frames before auto-advance (~1.5s)
PLAYER_W = 22
PLAYER_H = 34

# Lives / economy
MAX_HEARTS = 3
SPELL_FREEZE_TIME = 180  # frames (~3 sec at 60fps)
HELL_FREEZE_TIME = 75  # short freeze — must time it
HELL_HEART_CAP = 3  # excess hearts burn away at Hell's gate
HELL_SPELL_CAP = 4  # only a few spells survive the fire
HELL_FALL_DAMAGE = 2  # lava hits harder


# Colors
SKY = (140, 200, 235)
SKY_SOFT = (168, 216, 242)
CLOUD = (248, 252, 255)
CLOUD_EDGE = (220, 232, 240)
GRASS = (92, 176, 88)
GRASS_DARK = (70, 148, 70)
DIRT = (198, 160, 96)
DIRT_DARK = (168, 132, 78)
WATER = (56, 120, 176)
WATER_DEEP = (40, 96, 152)
WATER_FOAM = (210, 236, 248)
ICE = (220, 238, 248)
ICE_CRACK = (170, 200, 220)
ICE_LINE = (120, 160, 190)
DEER = (120, 78, 48)
TEXT = (36, 56, 72)
ACCENT = (220, 72, 72)
TREE_LEAF = (64, 148, 72)
TREE_LEAF_DARK = (48, 120, 58)
TREE_TRUNK = (120, 78, 48)
MUSHROOM_CAP = (220, 64, 64)
MUSHROOM_SPOT = (255, 255, 255)
MUSHROOM_STEM = (240, 230, 210)

# Pickup colors
HEART_COLOR = (220, 60, 70)
COIN_COLOR = (255, 200, 60)
SPELL_COLOR = (140, 100, 230)

# Hero
HERO_SKIN = (232, 196, 168)
HERO_HAIR = (78, 52, 40)
HERO_COAT = (176, 64, 56)
HERO_SCARF = (212, 148, 72)
HERO_PANTS = (72, 78, 96)
HERO_BOOTS = (56, 44, 36)

WATER_Y = 560

# Per-level spawn: (x, platform_top_y) — player stands on that ledge
SPAWNS = {
    1: (70, 520),
    2: (80, 520),
    3: (70, 520),
}
