"""Screen-space skies for the ten worlds on the street.

The road stays a straight line. This layer is what changes behind it:
forest, desert, moon, canyon, volcano, Saturn, storm, ice, asteroids,
and the black hole.
"""

from __future__ import annotations

import math
import random

import pygame

from .settings import SCREEN_H, SCREEN_W

PALETTES = {
    "GREEN FOREST": {
        "top": (92, 168, 232),
        "mid": (146, 206, 245),
        "bottom": (214, 236, 255),
        "sun_glow": (255, 236, 150),
        "sun_core": (255, 252, 230),
        "cloud": (255, 255, 255),
        "dune": (86, 168, 74),
        "ridge": (36, 112, 46),
        "cactus": None,
        "stars": False,
        "sun": "high",
        "scene": "forest",
    },
    "DESERT": {
        "top": (206, 86, 22),
        "mid": (236, 132, 32),
        "bottom": (255, 188, 74),
        "sun_glow": (255, 196, 80),
        "sun_core": (255, 244, 190),
        "cloud": (252, 168, 78),
        "dune": (228, 150, 72),
        "ridge": (176, 108, 48),
        "cactus": (42, 96, 38),
        "stars": False,
        "sun": "low",
        "scene": "desert",
    },
    "CRATER VALLEY": {
        "top": (8, 10, 22),
        "mid": (18, 22, 42),
        "bottom": (48, 52, 72),
        "sun_glow": (180, 186, 200),
        "sun_core": (230, 232, 236),
        "cloud": (60, 64, 84),
        "dune": (78, 80, 90),
        "ridge": (40, 42, 50),
        "cactus": None,
        "stars": True,
        "sun": "none",
        "scene": "moon",
    },
    "RED CANYON": {
        "top": (150, 48, 28),
        "mid": (196, 78, 36),
        "bottom": (232, 140, 72),
        "sun_glow": (255, 160, 70),
        "sun_core": (255, 220, 160),
        "cloud": (210, 120, 70),
        "dune": (176, 72, 40),
        "ridge": (110, 36, 28),
        "cactus": None,
        "stars": False,
        "sun": "low",
        "scene": "mars",
    },
    "VOLCANO": {
        "top": (28, 8, 12),
        "mid": (72, 18, 16),
        "bottom": (180, 48, 18),
        "sun_glow": (255, 80, 20),
        "sun_core": (255, 180, 60),
        "cloud": (78, 70, 66),
        "dune": (96, 30, 22),
        "ridge": (42, 16, 16),
        "cactus": None,
        "stars": False,
        "sun": "none",
        "scene": "volcano",
    },
    "RING HIGHWAY": {
        "top": (16, 14, 34),
        "mid": (42, 34, 62),
        "bottom": (88, 72, 96),
        "sun_glow": (255, 220, 160),
        "sun_core": (255, 244, 210),
        "cloud": (90, 78, 100),
        "dune": (120, 96, 70),
        "ridge": (62, 48, 36),
        "cactus": None,
        "stars": True,
        "sun": "none",
        "scene": "saturn",
    },
    "STORM WORLD": {
        "top": (64, 48, 42),
        "mid": (112, 78, 58),
        "bottom": (168, 122, 78),
        "sun_glow": (255, 200, 120),
        "sun_core": (255, 236, 190),
        "cloud": (86, 74, 66),
        "dune": (140, 96, 64),
        "ridge": (72, 48, 36),
        "cactus": None,
        "stars": False,
        "sun": "none",
        "scene": "jupiter",
    },
    "FROZEN STORM": {
        "top": (10, 28, 92),
        "mid": (22, 64, 148),
        "bottom": (90, 150, 206),
        "sun_glow": (180, 220, 255),
        "sun_core": (240, 248, 255),
        "cloud": (200, 220, 236),
        "dune": (110, 160, 198),
        "ridge": (214, 232, 244),
        "cactus": None,
        "stars": False,
        "sun": "none",
        "scene": "neptune",
    },
    "ASTEROID FIELD": {
        "top": (4, 6, 14),
        "mid": (10, 12, 24),
        "bottom": (22, 24, 36),
        "sun_glow": (200, 200, 210),
        "sun_core": (240, 240, 245),
        "cloud": (40, 40, 48),
        "dune": (36, 34, 32),
        "ridge": (18, 18, 22),
        "cactus": None,
        "stars": True,
        "sun": "none",
        "scene": "asteroid",
    },
    "BLACK HOLE": {
        "top": (4, 2, 12),
        "mid": (18, 6, 36),
        "bottom": (48, 12, 72),
        "sun_glow": (140, 60, 255),
        "sun_core": (255, 180, 255),
        "cloud": (70, 36, 100),
        "dune": (32, 14, 52),
        "ridge": (14, 6, 26),
        "cactus": None,
        "stars": True,
        "sun": "none",
        "scene": "blackhole",
    },
}


def _mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class WorldBackground:
    def __init__(self, stage):
        self.palette = PALETTES[stage["name"]]
        rng = random.Random(stage["seed"] + 999)
        self.stars = [(rng.randint(0, 2400), rng.randint(18, 280), rng.randint(1, 3)) for _ in range(90)]
        self.clouds = [
            (rng.randint(0, 2800), rng.randint(70, 250), rng.uniform(0.75, 1.55))
            for _ in range(11)
        ]
        self.cacti = [
            (180 + index * 760 + rng.randint(-40, 40), rng.uniform(0.75, 1.25))
            for index in range(8)
        ]
        self.trees = [
            (120 + index * 540 + rng.randint(-50, 50), rng.uniform(0.75, 1.35))
            for index in range(12)
        ]
        self.floaters = [
            (rng.randint(0, 2800), rng.randint(30, 460), rng.randint(7, 26), rng.uniform(0.35, 1.0))
            for _ in range(16)
        ]
        self.snow = [
            (rng.randint(0, SCREEN_W), rng.randint(0, SCREEN_H), rng.randint(1, 3))
            for _ in range(64)
        ]
        self.craters = [(rng.randint(60, 2400), rng.randint(16, 42)) for _ in range(8)]
        self.gradient = self._gradient()
        self.sun = self._sun() if self.palette["sun"] != "none" else None
        self.bands = self._bands()

    def _gradient(self):
        surface = pygame.Surface((SCREEN_W, SCREEN_H))
        top, mid, bottom = self.palette["top"], self.palette["mid"], self.palette["bottom"]
        for y in range(SCREEN_H):
            t = y / (SCREEN_H - 1)
            color = _mix(top, mid, t / 0.62) if t < 0.62 else _mix(mid, bottom, (t - 0.62) / 0.38)
            pygame.draw.line(surface, color, (0, y), (SCREEN_W, y))
        return surface

    def _sun(self):
        size = 220
        center = size // 2
        glow = self.palette["sun_glow"]
        core = self.palette["sun_core"]
        pixels = bytearray(size * size * 4)
        for y in range(size):
            for x in range(size):
                distance = math.hypot(x - center, y - center) / center
                if distance >= 1:
                    continue
                if distance < 0.11:
                    red, green, blue, alpha = 255, 252, 236, 255
                elif distance < 0.22:
                    blend = (distance - 0.11) / 0.11
                    red = int(255 + (core[0] - 255) * blend)
                    green = int(252 + (core[1] - 252) * blend)
                    blue = int(236 + (core[2] - 236) * blend)
                    alpha = 255
                else:
                    fade = (1 - distance) / 0.78
                    red, green, blue = glow
                    alpha = int(max(0, fade) ** 1.85 * 165)
                index = (y * size + x) * 4
                pixels[index:index + 4] = bytes((red, green, blue, alpha))
        image = pygame.image.frombuffer(pixels, (size, size), "RGBA").convert_alpha()
        return pygame.transform.smoothscale(image, (640, 640))

    def _bands(self):
        if self.palette["scene"] != "jupiter":
            return None
        surface = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for index in range(6):
            y = 48 + index * 52
            shade = 150 + (index % 2) * 28
            pygame.draw.rect(surface, (shade, 96, 68, 45), (0, y, SCREEN_W, 18))
        return surface

    def draw(self, surface, camera_x):
        scene = self.palette["scene"]
        now = pygame.time.get_ticks()
        surface.blit(self.gradient, (0, 0))
        if self.bands is not None:
            surface.blit(self.bands, (0, 0))
        self._sky_bodies(surface, camera_x, scene)
        self._weather(surface, camera_x, scene, now)
        self._ground(surface, camera_x, scene, now)

    def _sky_bodies(self, surface, camera_x, scene):
        if self.palette["stars"]:
            hole_x = SCREEN_W * 0.70 - camera_x * 0.006
            hole_y = 200
            for x, y, size in self.stars:
                screen_x = (x - camera_x * 0.04) % (SCREEN_W + 40) - 20
                draw_y = y
                if scene == "blackhole":
                    dx = screen_x - hole_x
                    dy = y - hole_y
                    bend = 70 / (math.hypot(dx, dy) + 1)
                    screen_x += dx * bend
                    draw_y += dy * bend
                pygame.draw.circle(surface, (230, 230, 236), (int(screen_x), int(draw_y)), size)
        if scene == "saturn":
            self._saturn(surface, camera_x)
        elif scene == "blackhole":
            self._black_hole(surface, camera_x)
        elif scene == "moon":
            earth_x = int(SCREEN_W - 150 - camera_x * 0.008)
            pygame.draw.circle(surface, (70, 130, 190), (earth_x, 96), 28)
            pygame.draw.circle(surface, (90, 160, 90), (earth_x - 8, 90), 10)
        sun_mode = self.palette["sun"]
        if sun_mode == "low":
            rect = self.sun.get_rect(center=(int(SCREEN_W * 0.56 - camera_x * 0.015), int(SCREEN_H * 0.62)))
            surface.blit(self.sun, rect)
        elif sun_mode == "high":
            small = pygame.transform.smoothscale(self.sun, (220, 220))
            surface.blit(small, small.get_rect(center=(int(SCREEN_W * 0.82 - camera_x * 0.01), 96)))

    def _weather(self, surface, camera_x, scene, now):
        if scene == "jupiter":
            self._lightning(surface, now)
        if scene not in ("moon", "asteroid", "blackhole", "saturn"):
            scale = 1.7 if scene == "jupiter" else 1.0
            for x, y, puff in self.clouds:
                self._puff(surface, (x - camera_x * 0.06) % 3200 - 300, y, puff * scale, self.palette["cloud"])
        if scene in ("saturn", "asteroid"):
            color = (110, 102, 92) if scene == "asteroid" else (150, 124, 86)
            for x, y, size, drift in self.floaters:
                screen_x = (x - camera_x * (0.05 + drift * 0.08)) % (SCREEN_W + 120) - 60
                bob = math.sin(now * 0.001 * drift + x) * 10
                self._rock(surface, screen_x, y + bob, size, color)
        if scene == "volcano":
            for x, y, size, speed in self.floaters[:9]:
                screen_x = (x - camera_x * 0.12) % (SCREEN_W + 40) - 20
                screen_y = (y + now * 0.06 * speed) % (SCREEN_H + 30) - 15
                self._rock(surface, screen_x, screen_y, max(5, size // 2), (70, 32, 24))

    def _ground(self, surface, camera_x, scene, now):
        far_amp = 70 if scene == "mars" else 46
        self._ridge(surface, camera_x, 0.12, SCREEN_H * 0.72, far_amp, 0.0045, 0.4, self.palette["dune"])
        self._ridge(surface, camera_x, 0.20, SCREEN_H * 0.80, 34, 0.006, 1.3, self.palette["ridge"])
        if scene == "forest":
            for x, scale in self.trees:
                screen_x = x - camera_x * 0.20
                if -80 < screen_x < SCREEN_W + 80:
                    self._tree(surface, screen_x, self._ground_y(x) + 4, scale)
        if self.palette["cactus"]:
            for x, scale in self.cacti:
                screen_x = x - camera_x * 0.20
                if -80 < screen_x < SCREEN_W + 80:
                    self._cactus(surface, screen_x, self._ground_y(x) + 6, scale, self.palette["cactus"])
        if scene == "moon":
            for x, radius in self.craters:
                screen_x = x - camera_x * 0.20
                if -40 < screen_x < SCREEN_W + 40:
                    ground = self._ground_y(x) - 8
                    pygame.draw.circle(surface, (28, 30, 36), (int(screen_x), int(ground)), radius)
                    pygame.draw.circle(surface, (90, 92, 100), (int(screen_x), int(ground)), radius, 2)
        if scene == "mars":
            for index, (_x, _y, size, _speed) in enumerate(self.floaters[:8]):
                world_x = 200 + index * 340
                screen_x = world_x - camera_x * 0.20
                if -40 < screen_x < SCREEN_W + 40:
                    self._rock(surface, screen_x, self._ground_y(world_x) - 4, size * 0.7, (120, 52, 32))
        if scene == "volcano":
            for index, place in enumerate((280, 920, 1680)):
                screen_x = place - camera_x * 0.16
                if -120 < screen_x < SCREEN_W + 120:
                    self._volcano(surface, screen_x, self._ground_y(place) + 10, 1.1 + index * 0.15)
        if scene == "neptune":
            for index in range(16):
                streak_y = (index * 42 + now * 0.03) % SCREEN_H
                streak_x = (index * 130 - now * 0.35) % (SCREEN_W + 220) - 80
                pygame.draw.line(surface, (170, 210, 240), (streak_x, streak_y), (streak_x + 78, streak_y - 10), 2)
            for index, (x, y, size) in enumerate(self.snow):
                flake_x = (x + now * 0.04 + index * 3) % SCREEN_W
                flake_y = (y + now * 0.08) % SCREEN_H
                pygame.draw.circle(surface, (236, 246, 255), (int(flake_x), int(flake_y)), size)

    def _ground_y(self, world_x):
        return self._ridge_y(world_x, SCREEN_H * 0.80, 34, 0.006, 1.3)

    def _ridge_y(self, world_x, base_y, amplitude, frequency, phase):
        y = base_y
        y += math.sin(world_x * frequency + phase) * amplitude
        y += math.sin(world_x * frequency * 2.3 + phase * 1.7) * amplitude * 0.28
        return y

    def _ridge(self, surface, camera_x, parallax, base_y, amplitude, frequency, phase, color):
        points = []
        for x in range(-30, SCREEN_W + 50, 18):
            points.append((x, self._ridge_y(x + camera_x * parallax, base_y, amplitude, frequency, phase)))
        points.append((SCREEN_W + 50, SCREEN_H + 40))
        points.append((-30, SCREEN_H + 40))
        pygame.draw.polygon(surface, color, points)

    def _puff(self, surface, x, y, scale, color):
        for offset_x, offset_y, radius in ((-46, 10, 26), (-12, -8, 38), (28, 4, 32), (58, 12, 22)):
            pygame.draw.circle(
                surface,
                color,
                (int(x + offset_x * scale), int(y + offset_y * scale)),
                max(2, int(radius * scale)),
            )

    def _cactus(self, surface, x, y, scale, color):
        body_w = int(16 * scale)
        body_h = int(54 * scale)
        arm = int(9 * scale)
        pygame.draw.rect(surface, color, (int(x), int(y - body_h), body_w, body_h), border_radius=7)
        pygame.draw.rect(surface, color, (int(x - 18 * scale), int(y - body_h + 22 * scale), int(18 * scale), arm), border_radius=4)
        pygame.draw.rect(surface, color, (int(x - 18 * scale), int(y - body_h + 8 * scale), arm, int(24 * scale)), border_radius=4)
        pygame.draw.rect(surface, color, (int(x + body_w), int(y - body_h + 30 * scale), int(16 * scale), arm), border_radius=4)
        pygame.draw.rect(surface, color, (int(x + body_w + 7 * scale), int(y - body_h + 16 * scale), arm, int(24 * scale)), border_radius=4)

    def _tree(self, surface, x, y, scale):
        width = int(10 * scale)
        height = int(26 * scale)
        pygame.draw.rect(surface, (78, 52, 28), (int(x - width / 2), int(y - height), width, height))
        pygame.draw.polygon(
            surface,
            (28, 122, 48),
            ((int(x - 22 * scale), int(y - height + 8)), (int(x), int(y - height - 46 * scale)), (int(x + 22 * scale), int(y - height + 8))),
        )
        pygame.draw.polygon(
            surface,
            (46, 158, 62),
            (
                (int(x - 16 * scale), int(y - height - 16 * scale)),
                (int(x), int(y - height - 62 * scale)),
                (int(x + 16 * scale), int(y - height - 16 * scale)),
            ),
        )

    def _rock(self, surface, x, y, size, color):
        pygame.draw.polygon(
            surface,
            color,
            (
                (int(x - size), int(y + size * 0.4)),
                (int(x - size * 0.4), int(y - size * 0.8)),
                (int(x + size * 0.5), int(y - size * 0.3)),
                (int(x + size), int(y + size * 0.5)),
            ),
        )

    def _saturn(self, surface, camera_x):
        center_x = int(SCREEN_W * 0.78 - camera_x * 0.008)
        center_y = 168
        pygame.draw.ellipse(surface, (186, 160, 112), (center_x - 250, center_y - 36, 500, 74), 10)
        pygame.draw.ellipse(surface, (230, 206, 150), (center_x - 190, center_y - 22, 380, 46), 6)
        pygame.draw.circle(surface, (214, 176, 112), (center_x, center_y), 54)
        pygame.draw.circle(surface, (186, 146, 86), (center_x, center_y), 54, 4)

    def _black_hole(self, surface, camera_x):
        center_x = int(SCREEN_W * 0.70 - camera_x * 0.006)
        center_y = 200
        glow = pygame.Surface((460, 460), pygame.SRCALPHA)
        pygame.draw.circle(glow, (70, 20, 140, 55), (230, 230), 210)
        pygame.draw.circle(glow, (120, 40, 210, 45), (230, 230), 120)
        surface.blit(glow, (center_x - 230, center_y - 230))
        pygame.draw.ellipse(surface, (255, 140, 50), (center_x - 190, center_y - 26, 380, 52), 8)
        pygame.draw.ellipse(surface, (255, 220, 140), (center_x - 130, center_y - 12, 260, 26), 4)
        pygame.draw.circle(surface, (2, 0, 6), (center_x, center_y), 34)
        pygame.draw.circle(surface, (160, 70, 255), (center_x, center_y), 40, 3)

    def _lightning(self, surface, now):
        phase = (now // 80) % 14
        if phase > 1:
            return
        bolt = (now // 900) % 4
        x = 180 + bolt * 200
        points = [(x, 24)]
        for step in range(7):
            x += int(math.sin(bolt * 2.1 + step * 1.7) * 26)
            points.append((x, 24 + step * 36))
        color = (255, 255, 230) if phase == 0 else (170, 190, 255)
        pygame.draw.lines(surface, color, False, points, 3)

    def _volcano(self, surface, x, base_y, scale):
        pygame.draw.polygon(
            surface,
            (48, 22, 20),
            (
                (int(x - 70 * scale), int(base_y)),
                (int(x - 12 * scale), int(base_y - 92 * scale)),
                (int(x + 12 * scale), int(base_y - 92 * scale)),
                (int(x + 70 * scale), int(base_y)),
            ),
        )
        pygame.draw.polygon(
            surface,
            (255, 96, 24),
            (
                (int(x - 12 * scale), int(base_y - 92 * scale)),
                (int(x), int(base_y - 118 * scale)),
                (int(x + 12 * scale), int(base_y - 92 * scale)),
            ),
        )
