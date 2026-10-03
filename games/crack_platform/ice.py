"""Ice lake grid: thickness, cracks, and breaking."""

import random

from settings import (
    COLS,
    ROWS,
    THICK_MAX_CRACKS,
    THIN_CHANCE,
    THIN_MAX_CRACKS,
)


class IceGrid:
    """ROWS x COLS tiles. First and last row are solid shore."""

    def __init__(self):
        self.tiles = []
        self._build()

    def _build(self):
        self.tiles = []
        for row in range(ROWS):
            line = []
            for col in range(COLS):
                if row == 0 or row == ROWS - 1:
                    # Solid ground — never cracks
                    line.append({"shore": True, "thin": False, "cracks": 0, "max": 99, "broken": False})
                else:
                    thin = random.random() < THIN_CHANCE
                    max_cracks = THIN_MAX_CRACKS if thin else THICK_MAX_CRACKS
                    line.append(
                        {
                            "shore": False,
                            "thin": thin,
                            "cracks": 0,
                            "max": max_cracks,
                            "broken": False,
                        }
                    )
            self.tiles.append(line)

    def get(self, row, col):
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.tiles[row][col]
        return None

    def crack(self, row, col):
        """Add one crack. Returns True if the ice just broke."""
        tile = self.get(row, col)
        if tile is None or tile["shore"] or tile["broken"]:
            return False
        tile["cracks"] += 1
        if tile["cracks"] >= tile["max"]:
            tile["broken"] = True
            return True
        return False

    def is_walkable(self, row, col):
        tile = self.get(row, col)
        if tile is None:
            return False
        return not tile["broken"]
