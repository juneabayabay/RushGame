"""Screen size and the eight courses.

Weight is gravity relative to a normal world. Light courses hang in the air.
Heavy courses drop fast. The finish is always reachable at a careful pace.
"""

SCREEN_W = 1280
SCREEN_H = 720
FPS = 60

# Distances are pixels. Time is seconds. World Y grows downward.
RIDE = 32.0
ACCEL = 520.0
BRAKE = 780.0
FRICTION = 40.0
MAX_SPEED = 780.0
AIR_TURN = 2.7
NORMAL_G = 1450.0

PLAYER_COLOR = (176, 80, 235)

# land: how far the bike may tilt and still stick, in radians.
# turn: how fast W and S rotate the bike. Light worlds turn slowly.
# gravity: pull in the air. Light hangs. Heavy snaps down.
LEVELS = (
    {
        "name": "EASY ROLL",
        "length": 2600,
        "amp": 26,
        "freq": 0.0032,
        "gaps": (),
        "land": 1.2,
        "gravity": 1450,
        "turn": 1.0,
        "blurb": "Normal weight. Learn the bike.",
    },
    {
        "name": "LIGHT AIR",
        "length": 3400,
        "amp": 36,
        "freq": 0.0034,
        "gaps": ((2000, 2360),),
        "land": 1.0,
        "gravity": 820,
        "turn": 0.72,
        "blurb": "Light. You hang. Level out before the shelf.",
    },
    {
        "name": "SOFT DRIFT",
        "length": 4200,
        "amp": 42,
        "freq": 0.0036,
        "gaps": ((1700, 2140), (3000, 3500)),
        "land": 0.9,
        "gravity": 700,
        "turn": 0.66,
        "blurb": "Lighter. A long float. Do not over-rotate.",
    },
    {
        "name": "EVEN WEIGHT",
        "length": 4600,
        "amp": 80,
        "freq": 0.0042,
        "gaps": ((1800, 2020), (3200, 3480)),
        "land": 0.75,
        "gravity": 1450,
        "turn": 1.0,
        "blurb": "Normal weight again. Match the wheels.",
    },
    {
        "name": "HEAVY DROP",
        "length": 4800,
        "amp": 90,
        "freq": 0.0044,
        "gaps": ((1900, 2060), (3400, 3580)),
        "land": 0.58,
        "gravity": 2200,
        "turn": 1.3,
        "blurb": "Heavy. One correction, then you hit.",
    },
    {
        "name": "HARD PULL",
        "length": 5200,
        "amp": 100,
        "freq": 0.0046,
        "gaps": ((1700, 1860), (3100, 3280), (4200, 4380)),
        "land": 0.48,
        "gravity": 2550,
        "turn": 1.45,
        "blurb": "Heavier. The ground comes up fast.",
    },
    {
        "name": "FEATHER",
        "length": 6200,
        "amp": 30,
        "freq": 0.003,
        "gaps": ((1600, 2140), (3200, 3820), (4700, 5340)),
        "land": 0.8,
        "gravity": 620,
        "turn": 0.6,
        "blurb": "Almost weightless. Time the rotation.",
    },
    {
        "name": "CRUSH",
        "length": 6400,
        "amp": 110,
        "freq": 0.0048,
        "gaps": ((1500, 1660), (2700, 2880), (4000, 4180), (5200, 5380)),
        "land": 0.4,
        "gravity": 2900,
        "turn": 1.55,
        "blurb": "Crushing weight. Land on the first try.",
    },
)


def weight_of(level: dict) -> tuple[str, tuple, float]:
    """Name, HUD color, and multiplier against a normal world."""
    mult = level["gravity"] / NORMAL_G
    if mult < 0.85:
        return "LIGHT", (130, 230, 255), mult
    if mult > 1.35:
        return "HEAVY", (255, 150, 90), mult
    return "NORMAL", (255, 228, 160), mult


def kmh(speed: float) -> int:
    return int(abs(speed) * 0.62)
