"""Three worlds: Earth (easy) → Heaven (medium) → Hell (hard)."""

from platforms import Platform
from pickups import Pickup


THEMES = {
    1: {
        "name": "Earth",
        "subtitle": "Nature of the Earth",
        "sky": (140, 200, 235),
        "sky_soft": (168, 216, 242),
        "cloud": (248, 252, 255),
        "cloud_edge": (220, 232, 240),
        "top": (92, 176, 88),
        "top_dark": (70, 148, 70),
        "body": (198, 160, 96),
        "body_dark": (168, 132, 78),
        "hazard": (56, 120, 176),
        "hazard_deep": (40, 96, 152),
        "hazard_foam": (210, 236, 248),
        "ice": (220, 238, 248),
        "ice_crack": (170, 200, 220),
        "ice_line": (120, 160, 190),
        "text": (36, 56, 72),
        "accent": (220, 72, 72),
        "goal_name": "deer",
        "hazard_name": "water",
        "hero_tier": 1,
    },
    2: {
        "name": "Heaven",
        "subtitle": "Realm of Light",
        "sky": (210, 230, 255),
        "sky_soft": (245, 248, 255),
        "cloud": (255, 255, 255),
        "cloud_edge": (200, 210, 240),
        "top": (255, 250, 230),
        "top_dark": (240, 220, 180),
        "body": (230, 235, 250),
        "body_dark": (190, 200, 230),
        "hazard": (160, 190, 230),
        "hazard_deep": (120, 160, 210),
        "hazard_foam": (255, 255, 255),
        "ice": (230, 245, 255),
        "ice_crack": (190, 210, 240),
        "ice_line": (150, 170, 210),
        "text": (50, 60, 100),
        "accent": (255, 190, 60),
        "goal_name": "angel deer",
        "hazard_name": "clouds below",
        "hero_tier": 2,
    },
    3: {
        "name": "Hell",
        "subtitle": "Realm of Fire",
        "sky": (50, 20, 30),
        "sky_soft": (90, 30, 35),
        "cloud": (80, 40, 40),
        "cloud_edge": (120, 50, 45),
        "top": (180, 60, 40),
        "top_dark": (140, 40, 30),
        "body": (70, 35, 35),
        "body_dark": (45, 22, 22),
        "hazard": (220, 80, 30),
        "hazard_deep": (160, 40, 20),
        "hazard_foam": (255, 180, 60),
        "ice": (120, 100, 130),
        "ice_crack": (90, 70, 100),
        "ice_line": (200, 120, 140),
        "text": (255, 220, 200),
        "accent": (255, 90, 50),
        "goal_name": "shadow deer",
        "hazard_name": "lava",
        "hero_tier": 3,
    },
}


def build_level(level_id):
    """Harder layouts as level rises: narrower ledges, faster movers, weaker ice."""
    if level_id == 1:
        # Easy path: ~75px rise each step, little X-overlap so you never bonk your head
        return [
            Platform(40, 520, 180, 28, "grass"),
            Platform(250, 445, 160, 28, "grass"),
            Platform(450, 370, 150, 28, "grass"),
            Platform(620, 300, 140, 28, "grass"),
            Platform(430, 230, 150, 28, "grass"),
            Platform(220, 165, 150, 28, "grass"),
            Platform(420, 110, 150, 28, "grass"),
            Platform(620, 95, 160, 30, "grass"),  # goal ledge (deer)
        ]
    if level_id == 2:
        # Heaven — medium challenge, safe start, jumps you can land
        return [
            Platform(40, 520, 180, 28, "grass"),
            Platform(260, 445, 150, 26, "grass"),
            Platform(450, 380, 130, 26, "moving", move_x=1.1, move_range=40),
            Platform(620, 320, 130, 26, "grass"),
            Platform(430, 255, 130, 26, "ice", ice_hits=4),
            Platform(230, 195, 140, 26, "grass"),
            Platform(420, 140, 140, 26, "moving", move_x=1.2, move_range=45),
            Platform(620, 100, 150, 28, "grass"),  # goal
        ]
    # Hell — brutal: tiny ledges, fast movers, ice that dies fast. Hard to win.
    return [
        # Start (only safe foothold)
        Platform(40, 520, 120, 26, "grass"),
        # --- SAFE-ish LEFT (still deadly: narrow + ice) ---
        Platform(30, 440, 70, 20, "ice", ice_hits=2),
        Platform(30, 360, 65, 20, "moving", move_x=1.6, move_range=35),
        Platform(30, 280, 60, 18, "ice", ice_hits=1),
        Platform(40, 200, 70, 20, "moving", move_x=1.8, move_range=40),
        Platform(160, 145, 70, 20, "ice", ice_hits=2),
        Platform(300, 115, 75, 20, "grass"),
        # --- RISK RIGHT (faster, thinner, richer) ---
        Platform(220, 475, 70, 18, "moving", move_x=2.4, move_range=70),
        Platform(380, 430, 55, 18, "ice", ice_hits=1),
        Platform(520, 385, 60, 18, "moving", move_x=2.6, move_range=65),
        Platform(680, 340, 50, 16, "ice", ice_hits=1),
        Platform(560, 285, 55, 18, "moving", move_x=2.5, move_range=55),
        Platform(700, 230, 50, 16, "ice", ice_hits=1),
        Platform(580, 175, 60, 18, "moving", move_x=2.3, move_range=50),
        Platform(700, 130, 55, 18, "ice", ice_hits=1),
        # Bridge (tempting shortcut — breaks almost instantly)
        Platform(250, 330, 80, 18, "ice", ice_hits=1),
        Platform(400, 250, 70, 18, "moving", move_x=2.2, move_range=60),
        # Final gauntlet before deer
        Platform(420, 100, 70, 18, "ice", ice_hits=1),
        Platform(530, 95, 60, 18, "moving", move_x=2.0, move_range=35),
        Platform(680, 90, 90, 24, "grass"),  # goal
    ]


def build_pickups(level_id):
    if level_id == 1:
        # Easy stockpile run — pickups sit on each safe ledge
        return [
            Pickup(110, 490, "heart"),
            Pickup(300, 415, "spell"),
            Pickup(500, 340, "heart"),
            Pickup(660, 270, "spell"),
            Pickup(480, 200, "heart"),
            Pickup(280, 135, "spell"),
            Pickup(480, 80, "heart"),
            Pickup(700, 65, "coin"),
        ]
    if level_id == 2:
        return [
            Pickup(120, 490, "heart"),
            Pickup(300, 415, "spell"),
            Pickup(500, 350, "coin"),
            Pickup(660, 290, "spell"),
            Pickup(480, 225, "heart"),
            Pickup(280, 165, "coin"),
            Pickup(480, 110, "spell"),
            Pickup(680, 70, "coin"),
        ]
    # Hell — scarce heals; risk path pays coins if you survive
    return [
        Pickup(60, 410, "spell"),
        Pickup(55, 250, "heart"),
        Pickup(320, 85, "spell"),
        Pickup(250, 445, "coin"),
        Pickup(400, 400, "coin"),
        Pickup(700, 310, "coin"),
        Pickup(720, 200, "spell"),
        Pickup(600, 145, "coin"),
        Pickup(430, 220, "coin"),
    ]
