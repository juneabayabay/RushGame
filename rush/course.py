"""Side-view dirt course. Gaps are the jumps. A ramp rises into each one."""

from __future__ import annotations

import math


class Course:
    def __init__(self, level: dict):
        self.level = level
        self.length = float(level["length"])
        self.gaps = level["gaps"]
        self.base = 560.0
        self.amp = float(level["amp"])
        self.freq = float(level["freq"])
        self.gravity = float(level["gravity"])
        self.land = float(level["land"])
        self.turn = float(level["turn"])

    def hill_y(self, x: float) -> float:
        fade_in = min(1.0, max(0.0, (x - 200.0) / 280.0))
        fade_out = min(1.0, max(0.0, (self.length - 160.0 - x) / 280.0))
        fade = min(fade_in, fade_out)
        hills = self.amp * math.sin(x * self.freq)
        hills += self.amp * 0.28 * math.sin(x * self.freq * 2.15 + 0.8)
        return self.base - hills * fade

    def ground(self, x: float) -> float | None:
        for start, end in self.gaps:
            if start < x < end:
                return None
            dist = start - x
            if 0.0 < dist <= 320.0:
                return self.base - 155.0 * (1.0 - dist / 320.0)
            if 320.0 < dist <= 580.0:
                blend = (580.0 - dist) / 260.0
                return self.hill_y(x) * (1.0 - blend) + self.base * blend
            if end <= x <= end + 260.0:
                return self.base
            after = x - (end + 260.0)
            if 0.0 < after < 220.0:
                blend = after / 220.0
                return self.base * (1.0 - blend) + self.hill_y(x) * blend
        return self.hill_y(x)

    def slope(self, x: float) -> float:
        """Ground angle in screen space. Positive means downhill to the right."""
        left = self.ground(x - 16.0)
        right = self.ground(x + 16.0)
        here = self.ground(x)
        if here is None:
            return 0.0
        if left is None:
            left = here
        if right is None:
            right = here
            left = self.ground(x - 16.0) or here
            return math.atan2(right - left, 16.0)
        return math.atan2(right - left, 32.0)

    def spans(self, x0: float, x1: float, step: float = 14.0):
        """Solid runs of (x, y) across the visible ground. Gaps split the runs."""
        runs = []
        run = []
        x = x0
        while x <= x1:
            y = self.ground(x)
            if y is None:
                if run:
                    runs.append(run)
                    run = []
            else:
                run.append((x, y))
            x += step
        if run:
            runs.append(run)
        return runs
