"""Menu, course flow, and the motorcycle step."""

from __future__ import annotations

import pygame

from .bike import Bike, Input
from .course import Course
from .settings import FPS, LEVELS, SCREEN_H, SCREEN_W, weight_of
from .view import View


def score_landing(air: float, error: float, limit: float, spin: float) -> tuple[int, str]:
    """Points for a real jump. A tiny hop scores nothing."""
    if air < 0.32:
        return 0, ""
    hang = int(air * 140)
    match = max(0.0, 1.0 - error / max(0.2, limit))
    clean = int(90 * match)
    turned = int(min(spin, 1.6) * 35)
    total = hang + clean + turned
    if match > 0.72 and air >= 0.55:
        label = "CLEAN HANG"
    elif match > 0.72:
        label = "CLEAN"
    elif air >= 0.7:
        label = "LONG AIR"
    else:
        label = "LANDED"
    return total, label


class Game:
    def __init__(self):
        self.time = 0.0
        self.race_time = 0.0
        self.state = "menu"
        self.quit_requested = False
        self.level_index = 0
        self.bike = Bike()
        self.course = Course(LEVELS[0])
        self.bike.reset(self.course)
        self.countdown = 0.0
        self.clear_t = 0.0
        self.toast_text = ""
        self.toast_t = 0.0
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.hinted_air = False
        self.score = 0
        self.level_score = 0
        self.run_time = 0.0
        self.shake = 0.0
        self._snap_camera()

    def level(self):
        return LEVELS[self.level_index]

    def handle(self, event):
        if event.type != pygame.KEYDOWN:
            return
        key = event.key
        if self.state == "menu":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_run()
            elif key == pygame.K_ESCAPE:
                self.quit_requested = True
        elif self.state == "race":
            if key == pygame.K_ESCAPE:
                self.state = "pause"
        elif self.state == "pause":
            if key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.state = "race"
            elif key == pygame.K_r:
                self._open_level()
            elif key == pygame.K_m:
                self.state = "menu"
        elif self.state == "failed":
            if key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                self._open_level()
            elif key == pygame.K_ESCAPE:
                self.state = "menu"
        elif self.state == "victory":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_run()
            elif key == pygame.K_ESCAPE:
                self.state = "menu"

    def start_run(self):
        self.level_index = 0
        self.score = 0
        self.level_score = 0
        self.run_time = 0.0
        self._open_level(keep_score=True)

    def _open_level(self, keep_score=False):
        if not keep_score:
            self.score -= self.level_score
        self.level_score = 0
        self.course = Course(self.level())
        self.bike.reset(self.course)
        self.countdown = 3.0
        self.race_time = 0.0
        self.clear_t = 0.0
        self.toast_t = 0.0
        self.hinted_air = False
        self.shake = 0.0
        self.state = "race"
        name, _color, mult = weight_of(self.level())
        self.toast(f"{name}  {mult:.2f}x")
        self._snap_camera()

    def toast(self, text: str):
        self.toast_text = text
        self.toast_t = 1.6

    def update(self, dt: float):
        dt = min(max(dt, 0.0), 0.05)
        if self.state == "pause":
            return
        self.time += dt
        self.toast_t = max(0.0, self.toast_t - dt)
        if self.shake > 0:
            self.shake = max(0.0, self.shake - dt * 16)
        if self.state == "menu":
            self._snap_camera()
            return
        if self.state == "clear":
            self.clear_t -= dt
            self._follow_camera(dt)
            if self.clear_t <= 0.0:
                self._advance()
            return
        if self.state in ("failed", "victory"):
            return

        if self.countdown > 0.0:
            self.countdown -= dt
            if self.countdown <= 0.0:
                self.countdown = 0.0
                self.toast("GO")
            self._follow_camera(dt)
            return

        self.race_time += dt
        self.run_time += dt
        keys = pygame.key.get_pressed()
        inp = Input(
            gas=keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_d] or keys[pygame.K_RIGHT],
            brake=keys[pygame.K_s] or keys[pygame.K_DOWN] or keys[pygame.K_a] or keys[pygame.K_LEFT],
        )
        was_air = not self.bike.grounded
        self.bike.update(dt, inp, self.course)
        if self.bike.just_landed:
            self._award_landing()
        if self.bike.crashed:
            self.toast(self.bike.crash_reason)
            self.state = "failed"
        elif not was_air and not self.bike.grounded and not self.hinted_air:
            self.hinted_air = True
            self.toast("W NOSE UP    S NOSE DOWN")
        elif self.bike.x >= self.course.length:
            self.toast("LEVEL CLEAR")
            self.state = "clear"
            self.clear_t = 1.3
        self._follow_camera(dt)

    def _award_landing(self):
        bike = self.bike
        bike.just_landed = False
        gained, label = score_landing(bike.land_air, bike.land_error, self.course.land, bike.land_spin)
        if gained <= 0:
            return
        self.score += gained
        self.level_score += gained
        self.toast(f"+{gained}  {label}")
        if self.course.gravity > 1800 and bike.land_air > 0.25:
            self.shake = min(11.0, 5.0 + self.course.gravity / 500.0)

    def _advance(self):
        if self.level_index >= len(LEVELS) - 1:
            self.state = "victory"
            return
        self.level_index += 1
        self._open_level(keep_score=True)

    def _snap_camera(self):
        self.cam_x = self.bike.x + 280.0
        self.cam_y = self.bike.y - 40.0

    def _follow_camera(self, dt: float):
        target_x = self.bike.x + 280.0
        target_y = self.bike.y - 40.0
        rate = min(1.0, dt * 4.5)
        self.cam_x += (target_x - self.cam_x) * rate
        self.cam_y += (target_y - self.cam_y) * rate


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Gravity Rush Racing")
    clock = pygame.time.Clock()
    game = Game()
    view = View(screen)

    while not game.quit_requested:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.quit_requested = True
            else:
                game.handle(event)
        game.update(dt)
        view.draw(game)
        pygame.display.flip()

    pygame.quit()
