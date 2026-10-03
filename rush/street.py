"""A straight street and the obstacles in its lanes.

Every spawn leaves a way through: an open lane, or a low bar you can jump.
The active goal changes what is placed ahead of the bike.
"""

from __future__ import annotations

import random

from .settings import CLEAR_Z, LANE_X


THEMES = {
    "forest": {"block": (78, 52, 28), "bar": (196, 132, 48)},
    "desert": {"block": (36, 110, 42), "bar": (214, 170, 70)},
    "moon": {"block": (150, 152, 160), "bar": (210, 210, 216)},
    "mars": {"block": (150, 64, 40), "bar": (214, 120, 64)},
    "volcano": {"block": (70, 28, 24), "bar": (255, 96, 28)},
    "saturn": {"block": (176, 146, 96), "bar": (230, 200, 140)},
    "jupiter": {"block": (120, 84, 62), "bar": (196, 140, 80)},
    "neptune": {"block": (170, 210, 230), "bar": (230, 246, 255)},
    "asteroid": {"block": (110, 104, 98), "bar": (170, 164, 150)},
    "blackhole": {"block": (40, 16, 64), "bar": (180, 80, 255)},
}


class Obstacle:
    def __init__(self, y: float, lanes: set[int], jumpable: bool):
        self.y = y
        self.lanes = lanes
        self.jumpable = jumpable
        self.resolved = False


class Street:
    def __init__(self, seed: int, level_index: int, scene: str):
        self.rng = random.Random(seed)
        self.level_index = level_index
        self.scene = scene
        self.theme = THEMES[scene]
        self.gap = max(270, 450 - level_index * 16)
        self.obstacles: list[Obstacle] = []
        self.next_y = 0.0
        self.pattern = "dodge"
        self.spawned = 0

    def reset(self, player_y: float, pattern: str):
        self.obstacles.clear()
        self.pattern = pattern
        self.spawned = 0
        self.next_y = player_y - 720
        self.ensure(player_y)

    def set_pattern(self, pattern: str):
        self.pattern = pattern

    def ensure(self, player_y: float):
        limit = player_y - 1750
        while self.next_y > limit:
            self._spawn()
            extra = 90 if self.pattern in ("speed", "distance", "boost") else 0
            self.next_y -= self.gap + extra

    def _spawn(self):
        lanes = set(range(len(LANE_X)))
        if self.pattern == "jump" and self.spawned % 2 == 1:
            obstacle = Obstacle(self.next_y, lanes, True)
        else:
            open_lane = self.rng.randrange(len(LANE_X))
            others = [index for index in lanes if index != open_lane]
            if self.pattern in ("speed", "distance") or self.rng.random() < 0.6:
                blocked = {self.rng.choice(others)}
            else:
                blocked = set(others)
            jumpable = self.pattern != "jump" and self.rng.random() < 0.12
            obstacle = Obstacle(self.next_y, blocked, jumpable)
        if obstacle.lanes == lanes and not obstacle.jumpable:
            obstacle.lanes.discard(1)
        self.obstacles.append(obstacle)
        self.spawned += 1

    def cull(self, player_y: float):
        self.obstacles = [item for item in self.obstacles if item.y < player_y + 420]

    def resolve(self, player) -> list[str]:
        events = []
        occupied = player.occupied_lanes()
        for obstacle in self.obstacles:
            if obstacle.resolved:
                continue
            if not (player.prev_y >= obstacle.y >= player.y):
                continue
            obstacle.resolved = True
            jumped = obstacle.jumpable and player.z >= CLEAR_Z
            if occupied & obstacle.lanes and not jumped:
                if player.invuln <= 0.0:
                    events.append("hit")
            else:
                events.append("dodge")
                if jumped and occupied & obstacle.lanes:
                    events.append("jump_clear")
                if player.boosting:
                    events.append("boost_clear")
        return events
