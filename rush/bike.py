"""Side-view motorcycle.

On the dirt it follows the slope. Off a ramp it is in the air: gravity pulls
it down, and gas or brake rotates it until the wheels meet the ground.
"""

from __future__ import annotations

import math

from pygame.math import Vector2

from .settings import ACCEL, AIR_TURN, BRAKE, FRICTION, MAX_SPEED, RIDE


class Input:
    def __init__(self, gas=False, brake=False):
        self.gas = gas
        self.brake = brake


def wrap(angle: float) -> float:
    return (angle + math.pi) % math.tau - math.pi


class Bike:
    def __init__(self):
        self.color = (176, 80, 235)
        self.reset_pose()

    def reset_pose(self):
        self.x = 140.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 0.0
        self.angle = 0.0
        self.grounded = True
        self.crashed = False
        self.crash_reason = ""
        self.air_time = 0.0
        self.air_spin = 0.0
        self.spin = 0.0
        self.just_landed = False
        self.land_air = 0.0
        self.land_error = 0.0
        self.land_spin = 0.0

    def reset(self, course):
        self.reset_pose()
        self.x = 140.0
        ground = course.ground(self.x)
        self.y = (ground if ground is not None else course.base) - RIDE
        self.angle = -course.slope(self.x)

    @property
    def pos(self) -> Vector2:
        return Vector2(self.x, self.y)

    def local(self, lx: float, ly: float) -> tuple[float, float]:
        """Bike space to world. Positive angle points the nose up."""
        c = math.cos(self.angle)
        s = math.sin(self.angle)
        return (self.x + lx * c + ly * s, self.y - lx * s + ly * c)

    def update(self, dt: float, inp: Input, course):
        dt = min(max(dt, 0.0), 0.05)
        if self.crashed:
            return
        if self.grounded:
            self._drive(dt, inp, course)
        else:
            self._fly(dt, inp, course)
        self.spin += abs(self.speed) * dt

    def _drive(self, dt: float, inp: Input, course):
        slope = course.slope(self.x)
        self.angle = -slope
        if inp.gas:
            self.speed += ACCEL * dt
        elif inp.brake:
            self.speed -= BRAKE * dt
        else:
            self.speed -= FRICTION * dt
        self.speed += math.sin(slope) * course.gravity * 0.42 * dt
        self.speed = max(-40.0, min(MAX_SPEED, self.speed))
        self.vx = math.cos(slope) * self.speed
        self.vy = math.sin(slope) * self.speed

        next_x = self.x + self.vx * dt
        ground = course.ground(next_x)
        flight_y = self.y + self.vy * dt + 0.5 * course.gravity * dt * dt
        if ground is None or flight_y + RIDE < ground - 28.0:
            self.grounded = False
            self.air_time = 0.0
            self.air_spin = 0.0
            self.just_landed = False
            self.x = next_x
            self.y = flight_y
            return
        self.x = next_x
        self.y = ground - RIDE
        self.angle = -course.slope(self.x)
        self.air_time = 0.0

    def _fly(self, dt: float, inp: Input, course):
        self.air_time += dt
        before = self.angle
        rate = AIR_TURN * course.turn
        if inp.gas:
            self.angle += rate * dt
        if inp.brake:
            self.angle -= rate * dt
        self.air_spin += abs(wrap(self.angle - before))
        self.vy += course.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self._try_land(course)
        if self.y > course.base + 260.0:
            self._crash("FELL")

    def _try_land(self, course):
        if self.vy < 40.0:
            return
        ground = course.ground(self.x)
        if ground is None:
            return
        lowest = min(self.local(lx, RIDE)[1] for lx in (-26.0, 30.0))
        if lowest < ground:
            return
        target = -course.slope(self.x)
        error = abs(wrap(self.angle - target))
        if error > course.land:
            self._crash("BAD LANDING")
            return
        self.just_landed = True
        self.land_air = self.air_time
        self.land_error = error
        self.land_spin = self.air_spin
        slope = course.slope(self.x)
        self.grounded = True
        self.angle = -slope
        self.y = ground - RIDE
        self.speed = self.vx * math.cos(slope) + self.vy * math.sin(slope)
        self.speed = max(80.0, min(MAX_SPEED, self.speed))
        self.vx = math.cos(slope) * self.speed
        self.vy = math.sin(slope) * self.speed
        self.air_time = 0.0

    def _crash(self, reason: str):
        self.crashed = True
        self.crash_reason = reason
        self.grounded = False
        self.speed = 0.0
