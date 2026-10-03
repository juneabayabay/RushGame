"""Platforms: solid, breakable ice, and moving ledges (theme-aware)."""

import pygame


class Platform:
    def __init__(
        self,
        x,
        y,
        w,
        h,
        kind="grass",
        move_x=0,
        move_range=0,
        ice_hits=3,
    ):
        self.home_x = float(x)
        self.x = float(x)
        self.y = float(y)
        self.w = w
        self.h = h
        self.kind = kind  # grass | ice | moving
        self.move_x = move_x
        self.move_range = move_range
        self.dir = 1
        self.ice_hits = ice_hits
        self.max_hits = ice_hits
        self.broken = False
        self.vx = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, frozen=False):
        self.vx = 0.0
        if self.broken:
            return
        if self.kind == "moving" and self.move_range > 0 and not frozen:
            self.x += self.move_x * self.dir
            self.vx = self.move_x * self.dir
            if self.x > self.home_x + self.move_range:
                self.x = self.home_x + self.move_range
                self.dir = -1
            elif self.x < self.home_x - self.move_range:
                self.x = self.home_x - self.move_range
                self.dir = 1

    def stand_on(self, frozen=False):
        if self.kind != "ice" or self.broken or frozen:
            return False
        self.ice_hits -= 1
        if self.ice_hits <= 0:
            self.broken = True
            return True
        return False

    def draw(self, surface, theme):
        if self.broken:
            return
        r = self.rect
        if self.kind == "ice":
            color = theme["ice"] if self.ice_hits > self.max_hits // 2 else theme["ice_crack"]
            pygame.draw.rect(surface, color, r, border_radius=4)
            pygame.draw.rect(surface, (255, 255, 255), r, 1, border_radius=4)
            cracks = self.max_hits - self.ice_hits
            for i in range(cracks):
                pygame.draw.line(
                    surface,
                    theme["ice_line"],
                    (r.x + 8, r.y + 6 + i * 5),
                    (r.right - 8, r.y + 12 + i * 4),
                    2,
                )
        else:
            pygame.draw.rect(surface, theme["body"], r, border_radius=3)
            pygame.draw.rect(
                surface,
                theme["body_dark"],
                (r.x, r.y + 12, r.w, max(0, r.h - 12)),
                border_radius=3,
            )
            pygame.draw.rect(surface, theme["top"], (r.x, r.y, r.w, 12), border_radius=3)
            for gx in range(r.x + 4, r.right, 10):
                pygame.draw.line(surface, theme["top_dark"], (gx, r.y + 10), (gx, r.y + 16), 2)
            if self.kind == "moving":
                mid = r.centery
                pygame.draw.polygon(
                    surface,
                    (255, 255, 255),
                    [(r.x + 8, mid), (r.x + 16, mid - 4), (r.x + 16, mid + 4)],
                )
                pygame.draw.polygon(
                    surface,
                    (255, 255, 255),
                    [(r.right - 8, mid), (r.right - 16, mid - 4), (r.right - 16, mid + 4)],
                )
