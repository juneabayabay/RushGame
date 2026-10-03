"""Everything drawn on screen. The run itself lives in game.py."""

from __future__ import annotations

import math

import pygame
from pygame.math import Vector2

from .settings import GOALS_PER_STAGE, LANE_X, PLAYER_COLOR, ROAD_HALF, SCREEN_H, SCREEN_W, kmh


class View:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_title = pygame.font.SysFont("consolas", 68, bold=True)
        self.font_large = pygame.font.SysFont("consolas", 40, bold=True)
        self.font_med = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 16)
        self.font_tiny = pygame.font.SysFont("consolas", 13)
        self.dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self.dim.fill((4, 6, 16, 150))

    def draw(self, game):
        game.backdrop.draw(self.screen, -game.player.y * 0.15)
        if game.state == "menu":
            self.screen.blit(self.dim, (0, 0))
            self._menu()
            return
        self._road(game)
        self._obstacles(game)
        self._player(game)
        self._particles(game)
        self._hud(game)
        self._toast(game)
        if game.state == "pause":
            self._pause()
        elif game.state == "analyze":
            self._analyze(game)
        elif game.state == "failed":
            self._failed(game)
        elif game.state == "victory":
            self._victory(game)
        elif game.countdown > 0.05:
            number = str(max(1, math.ceil(game.countdown)))
            self._text(self.font_title, number, (255, 255, 255), (SCREEN_W / 2, SCREEN_H / 2 - 20), center=True)

    def w2s(self, game, pos: Vector2) -> tuple:
        shake_x = math.sin(game.time * 70.0) * game.shake if game.shake > 0 else 0.0
        shake_y = math.cos(game.time * 53.0) * game.shake if game.shake > 0 else 0.0
        x = (pos.x - game.cam.x + shake_x) * game.zoom + SCREEN_W / 2
        y = (pos.y - game.cam.y + shake_y) * game.zoom + SCREEN_H / 2
        return (int(x), int(y))

    def _road(self, game):
        top = game.cam.y - 900
        bot = game.cam.y + 900
        corners = [
            Vector2(-ROAD_HALF, top),
            Vector2(ROAD_HALF, top),
            Vector2(ROAD_HALF, bot),
            Vector2(-ROAD_HALF, bot),
        ]
        pygame.draw.polygon(self.screen, (18, 22, 32), [self.w2s(game, p) for p in corners])
        edge = (0, 210, 200)
        pygame.draw.line(self.screen, edge, self.w2s(game, Vector2(-ROAD_HALF, top)), self.w2s(game, Vector2(-ROAD_HALF, bot)), 3)
        pygame.draw.line(self.screen, edge, self.w2s(game, Vector2(ROAD_HALF, top)), self.w2s(game, Vector2(ROAD_HALF, bot)), 3)
        for edge_x in (-90, 90):
            self._dashes(game, edge_x, top, bot)

    def _dashes(self, game, lane_x, top, bot):
        y = math.floor(top / 48) * 48
        color = (226, 232, 240)
        while y < bot:
            a = Vector2(lane_x, y)
            b = Vector2(lane_x, min(bot, y + 18))
            pygame.draw.line(self.screen, color, self.w2s(game, a), self.w2s(game, b), 2)
            y += 48

    def _obstacles(self, game):
        theme = game.street.theme
        for obstacle in game.street.obstacles:
            if obstacle.jumpable and obstacle.lanes == set(range(len(LANE_X))):
                left = self.w2s(game, Vector2(-ROAD_HALF + 28, obstacle.y))
                right = self.w2s(game, Vector2(ROAD_HALF - 28, obstacle.y))
                pygame.draw.line(self.screen, theme["bar"], left, right, max(4, int(10 * game.zoom)))
                continue
            for lane in obstacle.lanes:
                center = Vector2(LANE_X[lane], obstacle.y)
                self._block(game, center, theme["bar"] if obstacle.jumpable else theme["block"], obstacle.jumpable)

    def _block(self, game, center: Vector2, color, low: bool):
        if low:
            a = self.w2s(game, center + Vector2(-46, 8))
            b = self.w2s(game, center + Vector2(46, 8))
            pygame.draw.line(self.screen, color, a, b, max(3, int(8 * game.zoom)))
            return
        top = self.w2s(game, center + Vector2(0, -34))
        left = self.w2s(game, center + Vector2(-28, 16))
        right = self.w2s(game, center + Vector2(28, 16))
        pygame.draw.polygon(self.screen, color, (top, right, left))
        pygame.draw.polygon(self.screen, (240, 244, 248), (top, right, left), 1)

    def _player(self, game):
        player = game.player
        body = Vector2(player.lane_x, player.y - player.z)
        sx, sy = self.w2s(game, player.pos)
        sw, sh = max(8, int(36 * game.zoom)), max(4, int(14 * game.zoom))
        pygame.draw.ellipse(self.screen, (8, 10, 16), pygame.Rect(sx - sw // 2, sy - sh // 2, sw, sh))
        if len(player.trail) >= 2:
            last = len(player.trail) - 1
            for index in range(last):
                fade = (index + 1) / last
                shade = tuple(int(c * fade) for c in player.color)
                pygame.draw.line(
                    self.screen,
                    shade,
                    self.w2s(game, player.trail[index]),
                    self.w2s(game, player.trail[index + 1]),
                    2,
                )
        forward = Vector2(0, -1)
        lateral = Vector2(1, 0)
        color = (255, 240, 240) if player.invuln > 0 and int(game.time * 18) % 2 == 0 else player.color

        def pt(along, side):
            return self.w2s(game, body + forward * along + lateral * side)

        nose = [pt(26, 0), pt(8, 14), pt(-16, 12), pt(-22, 0), pt(-16, -12), pt(8, -14)]
        pygame.draw.polygon(self.screen, color, nose)
        pygame.draw.polygon(self.screen, (245, 250, 255), nose, 1)
        if player.boosting:
            pygame.draw.polygon(self.screen, (255, 220, 120), [pt(-22, 6), pt(-40, 0), pt(-22, -6)])

    def _particles(self, game):
        for speck in game.particles:
            fade = 1 - speck["age"] / speck["life"]
            color = tuple(int(c * fade) for c in speck["c"][:3])
            pygame.draw.circle(self.screen, color, self.w2s(game, speck["p"]), max(1, int(speck["s"] * fade)))

    def _hud(self, game):
        shade = pygame.Surface((SCREEN_W, 108), pygame.SRCALPHA)
        shade.fill((4, 6, 14, 150))
        self.screen.blit(shade, (0, SCREEN_H - 108))
        stage = game._stage()
        self._text(self.font_med, f"{game.stage_index + 1}/10   {stage['name']}", (232, 244, 255), (24, 16))
        if game.goal:
            step = f"{game.cleared + 1}/{GOALS_PER_STAGE}   {game.goal.hud}    {game.analyzer.progress_text(game.goal)}"
            self._text(self.font_sm, step, (255, 220, 140), (24, 48))
            need = game.analyzer.live_need(game.goal.kind, self._is_fast(game))
            if need and game.countdown <= 0:
                self._text(self.font_tiny, need, (255, 170, 120), (24, 72))
            self._status_bar(game)
        self._text(self.font_tiny, f"POINTS {game.points}", (180, 220, 210), (24, 96))
        self._text(self.font_large, str(kmh(game.player.speed)), game.player.color, (SCREEN_W - 180, SCREEN_H - 78))
        self._text(self.font_tiny, "KM/H", (160, 180, 190), (SCREEN_W - 180, SCREEN_H - 36))
        self._boost(game)
        if game.countdown <= 0 and game.callout_t <= 0 and game.state == "race":
            hint = "W SPEED    A / D LANE    SPACE JUMP    SHIFT BOOST"
            self._text(self.font_tiny, hint, (190, 210, 210), (SCREEN_W * 0.42, SCREEN_H - 18))

    def _is_fast(self, game) -> bool:
        if game.goal is None or game.goal.kind != "speed":
            return game.player.speed > 400
        return game.player.grounded and kmh(game.player.speed) >= game.goal.mark

    def _status_bar(self, game):
        goal = game.goal
        if goal is None:
            return
        width, height = 280, 12
        x, y = 460, 52
        pygame.draw.rect(self.screen, (12, 16, 28), (x, y, width, height), border_radius=3)
        ratio = max(0.0, goal.left / max(0.01, goal.limit))
        fill = (255, 64, 84) if goal.left < 3.5 else (70, 220, 190)
        if ratio > 0:
            pygame.draw.rect(self.screen, fill, (x, y, max(1, int(width * ratio)), height), border_radius=3)
        pygame.draw.rect(self.screen, (210, 230, 235), (x, y, width, height), 1, border_radius=3)
        self._text(self.font_tiny, f"STATUS {max(0.0, goal.left):.1f}s", (210, 230, 235), (x + width + 12, y - 2))

    def _boost(self, game):
        x, y = SCREEN_W - 420, SCREEN_H - 64
        width, height = 200, 14
        pygame.draw.rect(self.screen, (16, 20, 32), (x, y, width, height), border_radius=4)
        amount = max(0.0, min(1.0, game.player.boost / 100.0))
        fill = (255, 170, 50) if amount > 0.2 else (255, 70, 90)
        if amount > 0:
            pygame.draw.rect(self.screen, fill, (x, y, int(width * amount), height), border_radius=4)
        pygame.draw.rect(self.screen, (200, 220, 230), (x, y, width, height), 1, border_radius=4)
        self._text(self.font_tiny, "BOOST", (180, 190, 200), (x, y - 16))

    def _toast(self, game):
        if game.toast_t <= 0 or not game.toast_text:
            return
        alpha = min(1.0, game.toast_t / 0.25)
        color = tuple(int(c * alpha) for c in (255, 244, 220))
        self._text(self.font_large, game.toast_text, color, (SCREEN_W / 2, SCREEN_H * 0.30), center=True)

    def _panel(self, width, height):
        rect = pygame.Rect(0, 0, width, height)
        rect.center = (SCREEN_W // 2, SCREEN_H // 2)
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill((6, 10, 22, 215))
        self.screen.blit(panel, rect.topleft)
        pygame.draw.rect(self.screen, (0, 220, 210), rect, 1, border_radius=10)

    def _pause(self):
        self._panel(420, 200)
        self._text(self.font_large, "PAUSED", (255, 255, 255), (SCREEN_W / 2, SCREEN_H / 2 - 48), center=True)
        self._text(self.font_sm, "ENTER  RESUME", (200, 230, 230), (SCREEN_W / 2, SCREEN_H / 2 - 4), center=True)
        self._text(self.font_sm, "R  RETRY LEVEL     M  MENU", (200, 230, 230), (SCREEN_W / 2, SCREEN_H / 2 + 28), center=True)

    def _analyze(self, game):
        self._panel(640, 280)
        y = SCREEN_H / 2 - 90
        for index, line in enumerate(game.analyze_lines):
            font = self.font_large if index == 0 else self.font_med
            color = (255, 255, 255) if index == 0 else (255, 214, 140)
            self._text(font, line, color, (SCREEN_W / 2, y), center=True)
            y += 52 if index == 0 else 40
        label = f"NEXT  {game.next_name}" if game.next_name else "FINAL WORLD"
        self._text(self.font_sm, label, (160, 220, 210), (SCREEN_W / 2, y + 8), center=True)

    def _failed(self, game):
        self._panel(520, 220)
        goal = game.goal.hud if game.goal else ""
        self._text(self.font_large, "STATUS EXPIRED", (255, 90, 100), (SCREEN_W / 2, SCREEN_H / 2 - 60), center=True)
        self._text(self.font_sm, goal, (255, 220, 160), (SCREEN_W / 2, SCREEN_H / 2 - 16), center=True)
        self._text(self.font_sm, f"POINTS {game.points}", (180, 210, 220), (SCREEN_W / 2, SCREEN_H / 2 + 16), center=True)
        self._text(self.font_tiny, "R RETRY LEVEL     ESC MENU", (160, 190, 190), (SCREEN_W / 2, SCREEN_H / 2 + 52), center=True)

    def _victory(self, game):
        self._panel(560, 240)
        self._text(self.font_large, "STREET COMPLETE", (255, 255, 255), (SCREEN_W / 2, SCREEN_H / 2 - 60), center=True)
        self._text(self.font_med, f"POINTS  {game.points}", (180, 255, 210), (SCREEN_W / 2, SCREEN_H / 2 - 8), center=True)
        self._text(self.font_tiny, "ENTER RUNS IT AGAIN     ESC MENU", (160, 190, 190), (SCREEN_W / 2, SCREEN_H / 2 + 48), center=True)

    def _menu(self):
        header = pygame.Surface((SCREEN_W, 220), pygame.SRCALPHA)
        header.fill((5, 7, 16, 210))
        self.screen.blit(header, (0, 0))
        footer = pygame.Surface((SCREEN_W, 120), pygame.SRCALPHA)
        footer.fill((5, 7, 16, 230))
        self.screen.blit(footer, (0, SCREEN_H - 120))
        self._text(self.font_title, "GRAVITY RUSH", (245, 250, 255), (SCREEN_W / 2, 70), center=True)
        self._text(self.font_large, "RACING", PLAYER_COLOR, (SCREEN_W / 2, 128), center=True)
        self._text(self.font_sm, "ONE STREET    TEN WORLDS    DODGE TO ADVANCE", (220, 236, 245), (SCREEN_W / 2, 176), center=True)
        self._text(self.font_med, "ENTER TO RACE", (255, 255, 255), (SCREEN_W / 2, SCREEN_H - 78), center=True)
        self._text(
            self.font_tiny,
            "W SPEED    A / D LANE    SPACE JUMP    SHIFT BOOST    ESC QUIT",
            (190, 215, 220),
            (SCREEN_W / 2, SCREEN_H - 42),
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
