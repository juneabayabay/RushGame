"""Meaningful pickups: heart (life), coin (money), spell (freeze)."""

import math

import pygame

from settings import COIN_COLOR, HEART_COLOR, SPELL_COLOR


class Pickup:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind  # heart | coin | spell
        self.taken = False
        self.r = 12

    @property
    def rect(self):
        return pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)

    def draw(self, surface, tick):
        if self.taken:
            return
        bob = int(math.sin(tick * 0.1 + self.x * 0.05) * 3)
        cx, cy = self.x, self.y + bob
        if self.kind == "heart":
            pygame.draw.circle(surface, HEART_COLOR, (cx - 4, cy - 2), 5)
            pygame.draw.circle(surface, HEART_COLOR, (cx + 4, cy - 2), 5)
            pygame.draw.polygon(surface, HEART_COLOR, [(cx - 9, cy), (cx + 9, cy), (cx, cy + 9)])
        elif self.kind == "coin":
            pygame.draw.circle(surface, COIN_COLOR, (cx, cy), 9)
            pygame.draw.circle(surface, (255, 240, 160), (cx, cy), 9, 2)
            pygame.draw.circle(surface, (200, 140, 30), (cx, cy), 4)
        else:
            pygame.draw.circle(surface, SPELL_COLOR, (cx, cy), 10)
            pygame.draw.circle(surface, (220, 200, 255), (cx, cy), 10, 2)
            pygame.draw.polygon(
                surface,
                (255, 255, 255),
                [(cx, cy - 6), (cx + 4, cy + 2), (cx - 4, cy + 2)],
            )
