"""One timed goal at a time.

Each world has a lesson order taken from its sky. Hits, missed jumps, low
pace, or unused boost replace that lesson. The check before a sky change
reads the whole level, then the world that is about to arrive.
"""

from __future__ import annotations

from .settings import cruise_speed, kmh

SCENE_LESSON = {
    "forest": ("dodge", "jump", "speed", "distance"),
    "desert": ("dodge", "jump", "boost", "speed"),
    "moon": ("jump", "dodge", "distance", "boost"),
    "mars": ("dodge", "speed", "jump", "boost"),
    "volcano": ("jump", "dodge", "boost", "speed"),
    "saturn": ("boost", "dodge", "speed", "jump"),
    "jupiter": ("speed", "dodge", "boost", "jump"),
    "neptune": ("dodge", "speed", "jump", "distance"),
    "asteroid": ("jump", "dodge", "boost", "distance"),
    "blackhole": ("speed", "dodge", "jump", "boost"),
}

PHRASE = {
    "dodge": "YOU NEED CLEANER LINES",
    "jump": "YOU NEED TO LEAVE THE GROUND",
    "speed": "YOU NEED MORE PACE",
    "boost": "YOU NEED THE BOOST",
    "distance": "YOU HAVE THE LINE  ·  PUSH ON",
}


class Objective:
    def __init__(self, kind, hud, need, limit, bonus, mark=0):
        self.kind = kind
        self.hud = hud
        self.need = need
        self.limit = limit
        self.bonus = bonus
        self.mark = mark
        self.left = limit


class RunStats:
    def __init__(self):
        self.hits = 0
        self.dodges = 0
        self.jumps = 0
        self.jump_clears = 0
        self.boost_clears = 0
        self.speed_hold = 0.0
        self.speed_best = 0.0
        self.distance = 0.0


class Analyzer:
    def __init__(self):
        self.level = RunStats()
        self.window = RunStats()
        self._streak = 0.0

    def begin_level(self):
        self.level = RunStats()
        self.begin_window()

    def begin_window(self):
        self.window = RunStats()
        self._streak = 0.0

    def note(self, event: str):
        for stats in (self.window, self.level):
            if event == "hit":
                stats.hits += 1
            elif event == "dodge":
                stats.dodges += 1
            elif event == "jump":
                stats.jumps += 1
            elif event == "jump_clear":
                stats.jump_clears += 1
            elif event == "boost_clear":
                stats.boost_clears += 1

    def tick_speed(self, dt: float, fast: bool):
        if fast:
            self._streak += dt
            self.window.speed_hold = self._streak
            self.level.speed_best = max(self.level.speed_best, self._streak)
        else:
            self._streak = 0.0
            self.window.speed_hold = 0.0

    def tick_distance(self, amount: float):
        self.window.distance += amount
        self.level.distance += amount

    def live_need(self, kind: str, fast: bool) -> str | None:
        window = self.window
        if kind == "dodge" and window.hits >= 1:
            return "NEED  AN OPEN LANE"
        if kind == "jump" and window.jump_clears == 0:
            return "NEED  SPACE OVER THE LOW BAR"
        if kind == "speed" and not fast:
            return "NEED  MORE THROTTLE"
        if kind == "boost" and window.boost_clears == 0 and window.dodges >= 1:
            return "NEED  SHIFT AS YOU PASS"
        return None

    def kind_while_playing(self, scene: str, step: int, previous: str) -> str:
        if self.window.hits >= 2:
            return "dodge"
        lesson = SCENE_LESSON[scene]
        kind = lesson[min(step, len(lesson) - 1)]
        if kind == previous and self.window.hits == 0 and step + 1 < len(lesson):
            kind = lesson[step + 1]
        return kind

    def kind_before_change(self, next_scene: str) -> str:
        level = self.level
        if level.hits >= 3:
            return "dodge"
        if level.jumps == 0:
            return "jump"
        if level.speed_best < 0.45:
            return "speed"
        if level.boost_clears == 0:
            return "boost"
        return SCENE_LESSON[next_scene][0]

    def make(self, kind: str, level_index: int, gravity: float) -> Objective:
        pace = kmh(cruise_speed(gravity))
        if kind == "dodge":
            need = 4 + level_index
            return Objective("dodge", f"DODGE {need} OBSTACLES", need, 9 + need * 0.7, 50)
        if kind == "jump":
            need = 2 + level_index // 3
            return Objective("jump", f"JUMP {need} BARS", need, 12 + level_index * 0.4, 70)
        if kind == "speed":
            mark = max(280, int(pace * 0.90))
            return Objective("speed", f"HOLD {mark} KM/H", 0.70, 11, 80, mark=mark)
        if kind == "boost":
            need = 3 + level_index // 2
            return Objective("boost", f"BOOST PAST {need}", need, 12, 80)
        need = 1800 + level_index * 180
        return Objective("distance", "COVER THE NEXT STRETCH", need, 12, 60)

    def phrase(self, kind: str) -> str:
        return PHRASE[kind]

    def met(self, goal: Objective) -> bool:
        window = self.window
        if goal.kind == "dodge":
            return window.dodges >= goal.need
        if goal.kind == "jump":
            return window.jump_clears >= goal.need
        if goal.kind == "speed":
            return window.speed_hold >= goal.need
        if goal.kind == "boost":
            return window.boost_clears >= goal.need
        if goal.kind == "distance":
            return window.distance >= goal.need
        return False

    def progress_text(self, goal: Objective) -> str:
        window = self.window
        if goal.kind == "dodge":
            return f"{window.dodges}/{int(goal.need)}"
        if goal.kind == "jump":
            return f"{window.jump_clears}/{int(goal.need)}"
        if goal.kind == "speed":
            return f"{window.speed_hold:.1f} / 0.7s"
        if goal.kind == "boost":
            return f"{window.boost_clears}/{int(goal.need)}"
        if goal.kind == "distance":
            return f"{int(window.distance)}/{int(goal.need)}"
        return ""
