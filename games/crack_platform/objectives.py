"""Spring buds — collectibles that force longer paths on cracking ice."""

import random

import pygame

from settings import BUD_COUNT, COLS, ROWS, TILE


def spawn_buds(player_pos, deer_pos):
    """Place BUD_COUNT buds on random lake tiles (not shore, not start/goal)."""
    lake_tiles = [
        (r, c)
        for r in range(1, ROWS - 1)
        for c in range(COLS)
        if (r, c) != player_pos and (r, c) != deer_pos
    ]
    random.shuffle(lake_tiles)
    picks = lake_tiles[:BUD_COUNT]
    return [{"row": r, "col": c, "taken": False} for r, c in picks]


def try_collect(buds, row, col):
    """Pick up a bud on this tile. Returns True if one was collected."""
    for bud in buds:
        if not bud["taken"] and bud["row"] == row and bud["col"] == col:
            bud["taken"] = True
            return True
    return False


def remaining(buds):
    return sum(1 for b in buds if not b["taken"])


def collected_count(buds):
    return sum(1 for b in buds if b["taken"])


def draw_bud(surface, x, y, tick):
    """Glowing square bud (Zelda-like collectible look)."""
    pulse = 1 + 0.15 * abs((tick % 40) - 20) / 20
    size = int(14 * pulse)
    cx = x + TILE // 2
    cy = y + TILE // 2
    # Soft glow
    glow = pygame.Surface((size + 10, size + 10), pygame.SRCALPHA)
    pygame.draw.rect(glow, (255, 230, 120, 70), glow.get_rect(), border_radius=3)
    surface.blit(glow, (cx - (size + 10) // 2, cy - (size + 10) // 2))
    # Core gem
    rect = pygame.Rect(0, 0, size, size)
    rect.center = (cx, cy)
    pygame.draw.rect(surface, (255, 220, 80), rect, border_radius=2)
    pygame.draw.rect(surface, (255, 250, 200), rect, 1, border_radius=2)
    # Tiny sparkle
    pygame.draw.circle(surface, (255, 255, 255), (cx - 3, cy - 3), 2)
