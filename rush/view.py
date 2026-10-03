"""Side-view dirt, sky, and the motorcycle."""

from __future__ import annotations

import math

import pygame
from pygame.math import Vector2

from .settings import LEVELS, PLAYER_COLOR, SCREEN_H, SCREEN_W, kmh, weight_of


def fmt_time(value: float) -> str:
    minutes = int(value // 60)
    seconds = value - minutes * 60
    return f"{minutes:02}:{seconds:06.3f}"


class View:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_title = pygame.font.SysFont("consolas", 64, bold=True)
        self.font_large = pygame.font.SysFont("consolas", 40, bold=True)
        self.font_med = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 16)
        self.font_tiny = pygame.font.SysFont("consolas", 13)
        self.dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self.dim.fill((8, 16, 32, 90))

    def draw(self, game):
        self._sky(game)
        self._ground(game)
        self._flag(game)
        self._shadow(game)
        self._bike(game)
        if game.state == "menu":
            self.screen.blit(self.dim, (0, 0))
            self._menu(game)
            return
        self._hud(game)
        self._toast(game)
        if game.state == "pause":
            self._pause()
        elif game.state == "failed":
            self._failed(game)
        elif game.state == "victory":
            self._victory(game)
        elif game.countdown > 0.05:
            number = str(max(1, math.ceil(game.countdown)))
            self._text(self.font_title, number, (255, 255, 255), (SCREEN_W / 2, SCREEN_H / 2 - 40), center=True)

    def w2s(self, game, pos: Vector2) -> tuple:
        shake_x = math.sin(game.time * 72.0) * game.shake if game.shake else 0.0
        shake_y = math.cos(game.time * 54.0) * game.shake if game.shake else 0.0
        x = (pos.x - game.cam_x) + SCREEN_W / 2 + shake_x
        y = (pos.y - game.cam_y) + SCREEN_H / 2 + shake_y
        return (int(x), int(y))

    def _sky(self, game):
        name, _color, _mult = weight_of(game.level())
        if name == "LIGHT":
            top, bottom = (150, 214, 255), (226, 246, 255)
        elif name == "HEAVY":
            top, bottom = (32, 42, 78), (88, 108, 148)
        else:
            top, bottom = (92, 186, 245), (186, 228, 255)
        for y in range(SCREEN_H):
            t = y / (SCREEN_H - 1)
            color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_W, y))
        for index, (ox, oy, scale) in enumerate(((80, 70, 1.0), (420, 110, 1.3), (860, 60, 0.9), (1100, 140, 1.1))):
            drift = (game.cam_x * 0.15 + index * 40) % (SCREEN_W + 260)
            self._cloud(ox - drift + 200, oy, scale)

    def _cloud(self, x, y, scale):
        for dx, dy, radius in ((-40, 8, 22), (0, -6, 30), (36, 4, 24)):
            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                (int(x + dx * scale), int(y + dy * scale)),
                max(4, int(radius * scale)),
            )

    def _ground(self, game):
        x0 = game.cam_x - SCREEN_W
        x1 = game.cam_x + SCREEN_W
        bottom = game.course.base + 420
        dirt = (118, 76, 46) if game.level_index < 6 else (96, 58, 40)
        grass = (78, 176, 62) if game.level_index < 6 else (64, 140, 58)
        for run in game.course.spans(x0, x1):
            if len(run) < 2:
                continue
            poly = [self.w2s(game, Vector2(x, y)) for x, y in run]
            poly.append(self.w2s(game, Vector2(run[-1][0], bottom)))
            poly.append(self.w2s(game, Vector2(run[0][0], bottom)))
            pygame.draw.polygon(self.screen, dirt, poly)
            crest = [self.w2s(game, Vector2(x, y - 8)) for x, y in run]
            pygame.draw.lines(self.screen, grass, False, crest, 10)
            pygame.draw.lines(self.screen, (96, 196, 74), False, [self.w2s(game, Vector2(x, y - 2)) for x, y in run], 3)

    def _flag(self, game):
        ground = game.course.ground(game.course.length)
        if ground is None:
            return
        foot = self.w2s(game, Vector2(game.course.length, ground))
        top = self.w2s(game, Vector2(game.course.length, ground - 78))
        pygame.draw.line(self.screen, (40, 40, 48), foot, top, 3)
        pygame.draw.polygon(
            self.screen,
            (255, 70, 90),
            (top, (top[0] + 28, top[1] + 10), (top[0], top[1] + 20)),
        )

    def _shadow(self, game):
        ground = game.course.ground(game.bike.x)
        if ground is None:
            return
        sx, sy = self.w2s(game, Vector2(game.bike.x, ground))
        wide = 36 if game.bike.grounded else 22
        pygame.draw.ellipse(self.screen, (70, 46, 28), pygame.Rect(sx - wide, sy - 5, wide * 2, 10))

    def _bike(self, game):
        bike = game.bike

        def pt(lx, ly):
            x, y = bike.local(lx, ly)
            return self.w2s(game, Vector2(x, y))

        for lx in (-26, 30):
            center = pt(lx, 18)
            pygame.draw.circle(self.screen, (28, 30, 36), center, 15)
            pygame.draw.circle(self.screen, (210, 214, 220), center, 15, 3)
            pygame.draw.circle(self.screen, (170, 176, 186), center, 4)
        pygame.draw.line(self.screen, (70, 40, 90), pt(-26, 18), pt(8, 2), 4)
        pygame.draw.line(self.screen, (70, 40, 90), pt(30, 18), pt(10, 2), 4)
        pygame.draw.polygon(self.screen, PLAYER_COLOR, (pt(-18, 4), pt(22, 2), pt(16, -10), pt(-8, -8)))
        pygame.draw.line(self.screen, (120, 50, 170), pt(6, -6), pt(20, -2), 3)
        pygame.draw.line(self.screen, (90, 36, 140), pt(-2, -6), pt(2, -22), 5)
        pygame.draw.circle(self.screen, PLAYER_COLOR, pt(4, -30), 8)
        pygame.draw.circle(self.screen, (255, 220, 80), pt(8, -30), 3)
        if bike.crashed:
            pygame.draw.line(self.screen, (255, 80, 80), pt(-20, -20), pt(24, 16), 3)

    def _hud(self, game):
        level = game.level()
        name, weight_color, mult = weight_of(level)
        self._text(
            self.font_med,
            f"{game.level_index + 1}/{len(LEVELS)}   {level['name']}",
            (255, 255, 255),
            (24, 16),
        )
        self._text(self.font_sm, f"{name}  {mult:.2f}x", weight_color, (24, 44))
        self._text(self.font_tiny, f"SCORE {game.score}", (210, 245, 230), (24, 96))
        clock = fmt_time(game.race_time)
        badge = pygame.Surface((150, 36), pygame.SRCALPHA)
        badge.fill((20, 28, 40, 180))
        self.screen.blit(badge, (SCREEN_W / 2 - 75, 12))
        self._text(self.font_med, clock, (255, 236, 180), (SCREEN_W / 2, 30), center=True)
        done = min(1.0, max(0.0, game.bike.x / game.course.length))
        pygame.draw.rect(self.screen, (20, 28, 40), (24, 72, 280, 10), border_radius=4)
        pygame.draw.rect(self.screen, weight_color, (24, 72, int(280 * done), 10), border_radius=4)
        self._text(self.font_large, str(kmh(game.bike.speed)), (255, 255, 255), (SCREEN_W - 150, 18))
        self._text(self.font_tiny, "KM/H", (230, 236, 245), (SCREEN_W - 150, 58))
        if game.bike.grounded:
            hint = "W GAS     S BRAKE"
        else:
            hint = "IN THE AIR     W NOSE UP     S NOSE DOWN"
        self._text(self.font_tiny, hint, (255, 255, 255), (SCREEN_W / 2, SCREEN_H - 28), center=True)

    def _toast(self, game):
        if game.toast_t <= 0 or not game.toast_text:
            return
        alpha = min(1.0, game.toast_t / 0.25)
        color = tuple(int(c * alpha) for c in (255, 248, 230))
        self._text(self.font_large, game.toast_text, color, (SCREEN_W / 2, SCREEN_H * 0.28), center=True)

    def _panel(self, width, height):
        rect = pygame.Rect(0, 0, width, height)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2)
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill((16, 24, 40, 220))
        self.screen.blit(panel, rect.topleft)
        pygame.draw.rect(self.screen, (255, 196, 70), rect, 2, border_radius=12)

    def _pause(self):
        self._panel(440, 180)
        self._text(self.font_large, "PAUSED", (255, 255, 255), (SCREEN_W / 2, SCREEN_H / 2 - 40), center=True)
        self._text(self.font_sm, "ENTER  RESUME", (220, 230, 240), (SCREEN_W / 2, SCREEN_H / 2 + 4), center=True)
        self._text(self.font_sm, "R  RETRY     M  MENU", (220, 230, 240), (SCREEN_W / 2, SCREEN_H / 2 + 32), center=True)

    def _failed(self, game):
        self._panel(520, 220)
        reason = game.bike.crash_reason or "CRASH"
        self._text(self.font_large, reason, (255, 90, 100), (SCREEN_W / 2, SCREEN_H / 2 - 56), center=True)
        self._text(self.font_sm, game.level()["name"], (255, 220, 150), (SCREEN_W / 2, SCREEN_H / 2 - 16), center=True)
        self._text(self.font_sm, f"SCORE {game.score}", (190, 235, 220), (SCREEN_W / 2, SCREEN_H / 2 + 16), center=True)
        self._text(self.font_tiny, "R RETRY LEVEL     ESC MENU", (200, 210, 220), (SCREEN_W / 2, SCREEN_H / 2 + 52), center=True)

    def _victory(self, game):
        self._panel(560, 220)
        self._text(self.font_large, "COURSE COMPLETE", (255, 255, 255), (SCREEN_W / 2, SCREEN_H / 2 - 56), center=True)
        self._text(self.font_med, f"SCORE  {game.score}", (180, 255, 210), (SCREEN_W / 2, SCREEN_H / 2 - 12), center=True)
        self._text(self.font_sm, fmt_time(game.run_time), (255, 220, 140), (SCREEN_W / 2, SCREEN_H / 2 + 20), center=True)
        self._text(self.font_tiny, "ENTER RIDES IT AGAIN     ESC MENU", (200, 210, 220), (SCREEN_W / 2, SCREEN_H / 2 + 48), center=True)

    def _menu(self, game):
        self._text(self.font_title, "GRAVITY RUSH", (255, 255, 255), (SCREEN_W / 2, 78), center=True)
        self._text(self.font_large, "MOTO", PLAYER_COLOR, (SCREEN_W / 2, 132), center=True)
        self._text(self.font_sm, "LIGHT WORLDS HANG. HEAVY WORLDS DROP.", (240, 248, 255), (SCREEN_W / 2, 176), center=True)
        self._text(self.font_med, "ENTER TO RIDE", (255, 255, 255), (SCREEN_W / 2, SCREEN_H - 90), center=True)
        self._text(
            self.font_tiny,
            "W GAS AND NOSE UP     S BRAKE AND NOSE DOWN     ESC QUIT",
            (230, 236, 245),
            (SCREEN_W / 2, SCREEN_H - 52),
            center=True,
        )

    def _text(self, font, text, color, pos, center=False):
        image = font.render(text, True, color)
        shadow = font.render(text, True, (0, 0, 0))
        rect = image.get_rect()
        if center:
            rect.center = pos
        else:
            rect.topleft = pos
        self.screen.blit(shadow, rect.move(2, 2))
        self.screen.blit(image, rect)
