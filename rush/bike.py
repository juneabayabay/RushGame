"""Street bike. Forward is up the road. Lanes are left and right."""

from __future__ import annotations

from pygame.math import Vector2

from .settings import (
    ACCEL,
    BOOST_ACCEL,
    BOOST_DRAIN,
    BOOST_MAX_SPEED,
    BOOST_REGEN,
    BRAKE,
    FRICTION,
    GRAVITY,
    JUMP_SPEED,
    LANE_RESPONSE,
    LANE_X,
    PLAYER_COLOR,
    cruise_speed,
)


class Input:
    def __init__(self, accel=False, brake=False, steer=0.0, boost=False, jump=False):
        self.accel = accel
        self.brake = brake
        self.steer = steer
        self.boost = boost
        self.jump = jump


class Player:
    def __init__(self):
        self.color = PLAYER_COLOR
        self.gravity_scale = 1.0
        self.trail: list[Vector2] = []
        self._steer_held = False
        self.reset()

    def reset(self):
        self.y = 0.0
        self.prev_y = 0.0
        self.lane_index = 1
        self.lane_x = float(LANE_X[1])
        self.z = 0.0
        self.vz = 0.0
        self.speed = 0.0
        self.boost = 100.0
        self.boosting = False
        self.grounded = True
        self.invuln = 0.0
        self.shake = 0.0
        self.jumped = False
        self.trail.clear()
        self._steer_held = False

    @property
    def pos(self) -> Vector2:
        return Vector2(self.lane_x, self.y)

    def occupied_lanes(self) -> set[int]:
        lanes = {index for index, lane_x in enumerate(LANE_X) if abs(self.lane_x - lane_x) < 72}
        return lanes or {self.lane_index}

    def update(self, dt: float, inp: Input):
        dt = min(max(dt, 0.0), 0.05)
        self.prev_y = self.y
        self.jumped = False
        self.invuln = max(0.0, self.invuln - dt)
        self.boosting = bool(inp.boost and self.boost > 0.0)
        if self.boosting:
            self.boost = max(0.0, self.boost - BOOST_DRAIN * dt)
        else:
            self.boost = min(100.0, self.boost + BOOST_REGEN * dt)

        if inp.steer > 0.5:
            if not self._steer_held:
                self.lane_index = max(0, self.lane_index - 1)
                self._steer_held = True
        elif inp.steer < -0.5:
            if not self._steer_held:
                self.lane_index = min(len(LANE_X) - 1, self.lane_index + 1)
                self._steer_held = True
        else:
            self._steer_held = False

        target = LANE_X[self.lane_index]
        self.lane_x += (target - self.lane_x) * min(1.0, dt * LANE_RESPONSE)

        cruise = cruise_speed(self.gravity_scale)
        if inp.brake:
            self.speed -= BRAKE * dt
        elif inp.accel and self.boosting:
            self.speed = min(BOOST_MAX_SPEED, self.speed + (ACCEL + BOOST_ACCEL) * dt)
        elif inp.accel and self.speed < cruise:
            self.speed = min(cruise, self.speed + ACCEL * dt)
        elif not inp.accel:
            self.speed -= FRICTION * dt
        if not self.boosting and self.speed > cruise:
            self.speed = max(cruise, self.speed - 260.0 * dt)
        self.speed = max(0.0, self.speed)

        if inp.jump and self.grounded:
            self.vz = JUMP_SPEED
            self.grounded = False
            self.jumped = True

        if not self.grounded:
            self.vz -= GRAVITY * max(0.35, self.gravity_scale) * dt
            self.z += self.vz * dt
            if self.z <= 0.0:
                self.z = 0.0
                self.vz = 0.0
                self.grounded = True

        self.y -= self.speed * dt
        if self.speed > 160:
            self.trail.append(Vector2(self.pos))
            if len(self.trail) > 16:
                self.trail.pop(0)
        elif self.trail:
            self.trail.pop(0)

    def bump(self):
        self.speed *= 0.42
        self.invuln = 1.05
        self.shake = 9.0
        self.z = 0.0
        self.vz = 0.0
        self.grounded = True
