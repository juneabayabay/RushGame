"""Screen, street, and bike numbers."""

SCREEN_W = 1280
SCREEN_H = 720
FPS = 60

# Three lanes. Forward is world -Y, up the screen.
LANE_X = (-180, 0, 180)
ROAD_HALF = 300
CLEAR_Z = 28.0
GOALS_PER_STAGE = 4

GRAVITY = 2100.0
JUMP_SPEED = 640.0
ACCEL = 780.0
BRAKE = 1100.0
FRICTION = 80.0
MAX_SPEED = 1040.0
BOOST_ACCEL = 980.0
BOOST_MAX_SPEED = 1500.0
BOOST_DRAIN = 34.0
BOOST_REGEN = 14.0
LANE_RESPONSE = 9.0

PLAYER_COLOR = (0, 255, 220)

# `scene` picks obstacle shapes and the lesson order for that sky.
STAGES = (
    {"name": "GREEN FOREST", "scene": "forest", "gravity": 1.00, "seed": 10, "blurb": "Logs on the lane"},
    {"name": "DESERT", "scene": "desert", "gravity": 1.00, "seed": 15, "blurb": "Cactus in the lanes"},
    {"name": "CRATER VALLEY", "scene": "moon", "gravity": 0.55, "seed": 20, "blurb": "Long jumps, loose rock"},
    {"name": "RED CANYON", "scene": "mars", "gravity": 0.85, "seed": 30, "blurb": "Rocks in the dust"},
    {"name": "VOLCANO", "scene": "volcano", "gravity": 1.15, "seed": 40, "blurb": "Low bars and lava rock"},
    {"name": "RING HIGHWAY", "scene": "saturn", "gravity": 0.92, "seed": 70, "blurb": "Debris on the line"},
    {"name": "STORM WORLD", "scene": "jupiter", "gravity": 1.45, "seed": 60, "blurb": "Heavy air, tight gaps"},
    {"name": "FROZEN STORM", "scene": "neptune", "gravity": 1.20, "seed": 90, "blurb": "Ice in the lanes"},
    {"name": "ASTEROID FIELD", "scene": "asteroid", "gravity": 0.45, "seed": 100, "blurb": "Drifting rock"},
    {"name": "BLACK HOLE", "scene": "blackhole", "gravity": 1.35, "seed": 110, "blurb": "The last street"},
)


def cruise_speed(gravity: float) -> float:
    """Grip speed without boost. Light worlds cannot hold the same pace."""
    scale = max(0.2, gravity)
    return MAX_SPEED * min(1.08, max(0.64, 0.50 + 0.50 * scale))


def kmh(speed: float) -> int:
    return int(speed * 0.62)
