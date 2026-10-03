"""Run flow: menu, street, goals, and the read before the next sky."""

from __future__ import annotations

import math
import random

import pygame
from pygame.math import Vector2

from .bike import Input, Player
from .goals import Analyzer, Objective
from .settings import (
    BOOST_MAX_SPEED,
    FPS,
    GOALS_PER_STAGE,
    SCREEN_H,
    SCREEN_W,
    STAGES,
    cruise_speed,
    kmh,
)
from .sky import WorldBackground
from .street import Street
from .view import View


class Game:
    def __init__(self):
        self.time = 0.0
        self.state = "menu"
        self.quit_requested = False
        self.stage_index = 0
        self.points = 0
        self.cleared = 0
        self.goal: Objective | None = None
        self.analyzer = Analyzer()
        self.player = Player()
        self.street = Street(STAGES[0]["seed"], 0, STAGES[0]["scene"])
        self.callout_t = 0.0
        self.shake = 0.0
        self.toast_text = ""
        self.toast_t = 0.0
        self.jump_buffer = 0.0
        self.particles: list[dict] = []
        self.cam = Vector2()
        self.zoom = 1.0
        self.countdown = 0.0
        self.analyze_t = 0.0
        self.pending_goal: Objective | None = None
        self.pending_phrase = ""
        self.analyze_lines: list[str] = []
        self.next_name = ""
        self.backdrop = WorldBackground(STAGES[0])

    def _stage(self):
        return STAGES[self.stage_index]

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
            elif key == pygame.K_SPACE:
                self.jump_buffer = 0.14
        elif self.state == "pause":
            if key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.state = "race"
            elif key == pygame.K_r:
                self._restart_stage()
            elif key == pygame.K_m:
                self.state = "menu"
        elif self.state == "failed":
            if key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                self._restart_stage()
            elif key == pygame.K_ESCAPE:
                self.state = "menu"
        elif self.state == "victory":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_run()
            elif key == pygame.K_ESCAPE:
                self.state = "menu"

    def start_run(self):
        self.stage_index = 0
        self.points = 0
        self._open_stage(fresh_player=True)

    def _restart_stage(self):
        self._open_stage(fresh_player=True)

    def _open_stage(self, fresh_player: bool):
        stage = self._stage()
        if fresh_player:
            self.player.reset()
        self.player.gravity_scale = stage["gravity"]
        self.backdrop = WorldBackground(stage)
        self.street = Street(stage["seed"], self.stage_index, stage["scene"])
        self.analyzer.begin_level()
        self.cleared = 0
        kind = self.analyzer.kind_while_playing(stage["scene"], 0, "")
        self._arm(self.analyzer.make(kind, self.stage_index, stage["gravity"]))
        self.street.reset(self.player.y, self.goal.kind)
        self.countdown = 3.0
        self.jump_buffer = 0.0
        self.toast_t = 0.0
        self.shake = 0.0
        self.particles.clear()
        self.state = "race"
        self.cam = Vector2(0, self.player.y - 200)

    def _arm(self, goal: Objective):
        self.goal = goal
        self.analyzer.begin_window()
        self.street.set_pattern(goal.kind)
        self.callout_t = 1.4
        self.toast(goal.hud)

    def toast(self, text: str):
        self.toast_text = text
        self.toast_t = 1.45

    def update(self, dt: float):
        dt = min(max(dt, 0.0), 0.05)
        if self.state == "pause":
            return
        self.time += dt
        self.callout_t = max(0.0, self.callout_t - dt)
        self.toast_t = max(0.0, self.toast_t - dt)
        self.jump_buffer = max(0.0, self.jump_buffer - dt)
        self._update_particles(dt)
        if self.shake > 0:
            self.shake = max(0.0, self.shake - dt * 18)

        if self.state == "menu":
            return
        if self.state == "analyze":
            self.analyze_t -= dt
            if self.analyze_t <= 0:
                self._finish_analyze()
            return
        if self.state in ("failed", "victory"):
            return

        keys = pygame.key.get_pressed()
        racing = self.countdown <= 0 and self.state == "race"
        steer = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            steer += 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            steer -= 1.0
        inp = Input(
            accel=racing and (keys[pygame.K_w] or keys[pygame.K_UP]),
            brake=racing and (keys[pygame.K_s] or keys[pygame.K_DOWN]),
            steer=steer if racing else 0.0,
            boost=racing and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]),
            jump=racing and self.jump_buffer > 0.0,
        )

        if self.countdown > 0:
            self.countdown -= dt
            if self.countdown <= 0:
                self.countdown = 0
                self.toast("GO")
        else:
            self.player.update(dt, inp)
            if self.player.jumped:
                self.jump_buffer = 0.0
                self.analyzer.note("jump")
            if self.player.shake:
                self.shake = max(self.shake, self.player.shake)
                self.player.shake = 0.0
            for event in self.street.resolve(self.player):
                self.analyzer.note(event)
                if event == "hit":
                    self.player.bump()
                    self.shake = max(self.shake, self.player.shake)
                    self.player.shake = 0.0
                    self.toast("HIT")
                    self.burst(self.player.pos, (255, 80, 70), 12, 220)
            self.street.ensure(self.player.y)
            self.street.cull(self.player.y)
            speed_kmh = kmh(self.player.speed)
            self.analyzer.tick_speed(dt, self.player.grounded and speed_kmh >= self._pace_mark())
            self.analyzer.tick_distance(self.player.speed * dt)
            if self.player.boosting:
                tail = self.player.pos + Vector2(0, 22)
                if random.random() < 0.65:
                    self.burst(tail, (255, 210, 90), 2, 80)
            self._tick_goal(dt)

        self._follow_camera(dt)

    def _pace_mark(self) -> int:
        if self.goal and self.goal.kind == "speed":
            return self.goal.mark
        return int(kmh(cruise_speed(self._stage()["gravity"])) * 0.90)

    def _tick_goal(self, dt: float):
        goal = self.goal
        if goal is None or self.state != "race":
            return
        goal.left -= dt
        if self.analyzer.met(goal):
            self.points += goal.bonus
            self.player.boost = min(100.0, self.player.boost + 18)
            self.cleared += 1
            self.burst(self.player.pos, (230, 255, 220), 10, 160)
            if self.cleared >= GOALS_PER_STAGE:
                self._enter_analyze()
            else:
                kind = self.analyzer.kind_while_playing(self._stage()["scene"], self.cleared, goal.kind)
                self._arm(self.analyzer.make(kind, self.stage_index, self._stage()["gravity"]))
            return
        if goal.left <= 0:
            goal.left = 0
            self.toast("STATUS EXPIRED")
            self.state = "failed"

    def _enter_analyze(self):
        last = self.stage_index >= len(STAGES) - 1
        if last:
            kind = self.analyzer.kind_before_change(self._stage()["scene"])
            self.next_name = ""
        else:
            nxt = STAGES[self.stage_index + 1]
            kind = self.analyzer.kind_before_change(nxt["scene"])
            self.pending_goal = self.analyzer.make(kind, self.stage_index + 1, nxt["gravity"])
            self.next_name = nxt["name"]
        self.pending_phrase = self.analyzer.phrase(kind)
        level = self.analyzer.level
        self.analyze_lines = [
            "READING YOUR RUN",
            f"HITS {level.hits}    DODGES {level.dodges}    JUMPS {level.jumps}",
            self.pending_phrase,
        ]
        self.analyze_t = 2.8
        self.state = "analyze"
        self.goal = None

    def _finish_analyze(self):
        if self.stage_index >= len(STAGES) - 1:
            self.state = "victory"
            return
        self.stage_index += 1
        stage = self._stage()
        self.player.gravity_scale = stage["gravity"]
        self.backdrop = WorldBackground(stage)
        self.street = Street(stage["seed"], self.stage_index, stage["scene"])
        self.analyzer.begin_level()
        self.cleared = 0
        goal = self.pending_goal or self.analyzer.make("dodge", self.stage_index, stage["gravity"])
        self.street.reset(self.player.y, goal.kind)
        self.countdown = 0.0
        self._arm(goal)
        self.state = "race"

    def _follow_camera(self, dt):
        target = Vector2(0, self.player.y - 200)
        self.cam += (target - self.cam) * min(1.0, dt * 4.0)
        speed = self.player.speed
        target_zoom = 1.02 - min(0.10, speed / BOOST_MAX_SPEED * 0.10)
        self.zoom += (target_zoom - self.zoom) * min(1.0, dt * 2.2)

    def burst(self, pos, color, count, speed):
        for _ in range(count):
            angle = random.random() * math.tau
            mag = random.uniform(speed * 0.25, speed)
            self.particles.append(
                {
                    "p": Vector2(pos),
                    "v": Vector2(math.cos(angle), math.sin(angle)) * mag,
                    "life": random.uniform(0.16, 0.38),
                    "age": 0.0,
                    "c": color,
                    "s": random.randint(2, 4),
                }
            )

    def _update_particles(self, dt):
        alive = []
        for speck in self.particles:
            speck["age"] += dt
            if speck["age"] >= speck["life"]:
                continue
            speck["p"] += speck["v"] * dt
            speck["v"] *= 0.94
            alive.append(speck)
        self.particles = alive


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
