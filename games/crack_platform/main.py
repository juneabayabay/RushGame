

import sys

import pygame

from hero import draw_hero
from levels import THEMES, build_level, build_pickups
from settings import (
    ACCEL,
    AIR_CONTROL,
    COIN_COLOR,
    COYOTE_FRAMES,
    FPS,
    FRICTION,
    GRAVITY,
    HEART_COLOR,
    HEIGHT,
    HELL_FALL_DAMAGE,
    HELL_FREEZE_TIME,
    HELL_HEART_CAP,
    HELL_SPELL_CAP,
    JUMP_VELOCITY,
    MAX_FALL,
    MAX_HEARTS,
    MOVE_SPEED,
    NEXT_LEVEL_DELAY,
    PLAYER_H,
    PLAYER_W,
    SPAWNS,
    SPELL_COLOR,
    SPELL_FREEZE_TIME,
    TITLE,
    WATER_Y,
    WIDTH,
)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("segoeui", 26, bold=True)
        self.small = pygame.font.SysFont("segoeui", 15)
        self.hud = pygame.font.SysFont("segoeui", 16, bold=True)
        self.tick = 0
        self.level = 1
        self.money = 0
        self.spells = 1
        self.clouds = [
            {"x": 60.0, "y": 40, "w": 70, "h": 26, "speed": 0.15},
            {"x": 300.0, "y": 24, "w": 88, "h": 30, "speed": 0.1},
            {"x": 540.0, "y": 50, "w": 64, "h": 22, "speed": 0.12},
        ]
        self.load_level(1, full_reset=True)

    def load_level(self, level_id, full_reset=False):
        self.level = level_id
        self.theme = THEMES[level_id]
        self.platforms = build_level(level_id)
        self.pickups = build_pickups(level_id)
        self._build_sky()
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.coyote = COYOTE_FRAMES
        self.facing_right = True
        if full_reset:
            self.money = 0
            self.spells = 0
            self.hearts = MAX_HEARTS
        elif level_id > 1:
            if level_id == 3:
                # Hell burns excess — stockpile helps, but not an easy win
                self.hearts = min(self.hearts, HELL_HEART_CAP)
                self.spells = min(self.spells, HELL_SPELL_CAP)
            else:
                self.hearts = max(self.hearts, MAX_HEARTS)
                self.spells += 1
        else:
            self.hearts = max(self.hearts, MAX_HEARTS)
        self.freeze_timer = 0
        self.next_timer = 0
        self.state = "playing"
        # Stand firmly on the first platform (fixes auto-fall into hazard)
        sx, platform_top = SPAWNS[level_id]
        self.spawn = (float(sx), float(platform_top - PLAYER_H))
        self.pos_x, self.pos_y = self.spawn
        self.player = pygame.Rect(int(self.pos_x), int(self.pos_y), PLAYER_W, PLAYER_H)
        self.on_ground = True
        self.standing_on = self.platforms[0] if self.platforms else None
        if level_id == 1:
            self.message = "Earth is safe — collect hearts & spells. Save them for later!"
        elif level_id == 2:
            self.message = "Heaven — use spells (F) on moving clouds if needed."
        elif level_id == 3:
            self.message = "Hell is merciless. Excess hearts burn. Time your spells."
        else:
            self.message = f"Lv{level_id} {self.theme['name']}: {self.theme['subtitle']}"
        pygame.display.set_caption(f"{TITLE} — {self.theme['name']}")

    def _sync_rect(self):
        self.player.x = int(round(self.pos_x))
        self.player.y = int(round(self.pos_y))

    def _build_sky(self):
        t = self.theme
        self.sky = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            u = y / HEIGHT
            c = (
                int(t["sky"][0] + (t["sky_soft"][0] - t["sky"][0]) * u),
                int(t["sky"][1] + (t["sky_soft"][1] - t["sky"][1]) * u),
                int(t["sky"][2] + (t["sky_soft"][2] - t["sky"][2]) * u),
            )
            pygame.draw.line(self.sky, c, (0, y), (WIDTH, y))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r:
                    if self.state == "lose":
                        # Retry — keep money; Hell stays harsh on lives/spells
                        kept_spells = self.spells
                        kept_money = self.money
                        self.load_level(self.level, full_reset=False)
                        self.money = kept_money
                        if self.level == 3:
                            self.hearts = HELL_HEART_CAP
                            self.spells = min(kept_spells, HELL_SPELL_CAP)
                        else:
                            self.spells = kept_spells
                            self.hearts = max(MAX_HEARTS, self.hearts)
                    elif self.state == "all_clear":
                        self.load_level(1, full_reset=True)
                if self.state != "playing":
                    continue
                if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    if self.on_ground or self.coyote > 0:
                        self.vel_y = JUMP_VELOCITY
                        self.on_ground = False
                        self.coyote = 0
                if event.key == pygame.K_f:
                    self._cast_spell()
        return True

    def _go_next(self):
        if self.level >= 3:
            self.state = "all_clear"
            self.message = f"All realms cleared! Money {self.money}. Press R to replay."
            return
        nxt = self.level + 1
        self.load_level(nxt, full_reset=False)
        saved = f"Hearts {self.hearts} · Spells {self.spells}"
        self.message = f"Level up! {THEMES[nxt]['name']} — {saved}"

    def _cast_spell(self):
        if self.spells <= 0:
            self.message = "No spells left. Find a purple orb."
            return
        self.spells -= 1
        self.freeze_timer = HELL_FREEZE_TIME if self.level == 3 else SPELL_FREEZE_TIME
        if self.level == 3:
            self.message = "Frost fades fast here — move NOW!"
        else:
            self.message = "Frost Spell! Platforms frozen."

    def _move_axis(self, dx, dy):
        self.pos_x += dx
        self.pos_y += dy
        self._sync_rect()

        if self.player.left < 0:
            self.pos_x = 0
            self.vel_x = 0
        if self.player.right > WIDTH:
            self.pos_x = WIDTH - PLAYER_W
            self.vel_x = 0
        self._sync_rect()

        self.on_ground = False
        self.standing_on = None

        for p in self.platforms:
            if p.broken or not self.player.colliderect(p.rect):
                continue
            if dy > 0 and self.player.bottom - dy <= p.rect.top + 8:
                self.pos_y = p.rect.top - PLAYER_H
                self.vel_y = 0
                self.on_ground = True
                self.standing_on = p
                self.coyote = COYOTE_FRAMES
            elif dy < 0 and self.player.top - dy >= p.rect.bottom - 8:
                self.pos_y = p.rect.bottom
                self.vel_y = 0
            elif dx > 0:
                self.pos_x = p.rect.left - PLAYER_W
                self.vel_x = 0
            elif dx < 0:
                self.pos_x = p.rect.right
                self.vel_x = 0
            self._sync_rect()

    def update(self):
        # Auto-advance to next realm after clearing a stage
        if self.state == "level_clear":
            self.next_timer -= 1
            if self.next_timer <= 0:
                self._go_next()
            return

        if self.state != "playing":
            return

        if self.freeze_timer > 0:
            self.freeze_timer -= 1
            if self.freeze_timer == 0:
                self.message = "Frost wore off."

        frozen = self.freeze_timer > 0
        for p in self.platforms:
            p.update(frozen=frozen)

        keys = pygame.key.get_pressed()
        accel = ACCEL if self.on_ground else ACCEL * AIR_CONTROL
        moving = False
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel_x -= accel
            self.facing_right = False
            moving = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel_x += accel
            self.facing_right = True
            moving = True

        # Soft friction when not holding a direction
        if not moving:
            self.vel_x *= FRICTION if self.on_ground else 0.92
            if abs(self.vel_x) < 0.08:
                self.vel_x = 0.0

        self.vel_x = max(-MOVE_SPEED, min(MOVE_SPEED, self.vel_x))

        # Short jump if release early (smoother control)
        if self.vel_y < -3 and not (
            keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
        ):
            self.vel_y *= 0.88

        if self.on_ground and self.standing_on and self.standing_on.kind == "moving":
            self.pos_x += self.standing_on.vx

        if self.coyote > 0 and not self.on_ground:
            self.coyote -= 1

        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL)
        self._move_axis(self.vel_x, 0)
        self._move_axis(0, self.vel_y)

        crack_rate = 8 if self.level == 3 else (18 if self.level == 2 else 45)
        if self.on_ground and self.standing_on and self.tick % crack_rate == 0:
            if self.standing_on.stand_on(frozen=frozen):
                self.message = "It broke! Jump!"
                self.on_ground = False

        for item in self.pickups:
            if item.taken or not self.player.colliderect(item.rect):
                continue
            item.taken = True
            if item.kind == "heart":
                self.hearts = min(self.hearts + 1, 10)
                if self.level == 1:
                    self.message = "Heart saved for later levels!"
                else:
                    self.message = "Heart! Extra life."
            elif item.kind == "coin":
                self.money += 10 * self.level
                self.message = f"Coin! Money: {self.money}."
            else:
                self.spells += 1
                if self.level == 1:
                    self.message = "Spell stocked — save it for Heaven/Hell (F)."
                else:
                    self.message = "Spell! Press F to freeze."

        if self.player.top > WATER_Y:
            self._fall()

        goal = pygame.Rect(690, 55, 90, 55)
        if self.player.colliderect(goal):
            if self.level >= 3:
                self.state = "all_clear"
                self.message = f"Hell conquered! Money {self.money}. Press R to replay."
            else:
                self.state = "level_clear"
                self.next_timer = NEXT_LEVEL_DELAY
                nxt = THEMES[self.level + 1]["name"]
                self.message = f"{self.theme['name']} cleared! Stockpile ready — entering {nxt}..."

    def _fall(self):
        dmg = HELL_FALL_DAMAGE if self.level == 3 else 1
        self.hearts -= dmg
        if self.hearts <= 0:
            self.hearts = 0
            self.state = "lose"
            self.message = f"Fell into {self.theme['hazard_name']}. Press R to retry."
            return
        self.pos_x, self.pos_y = self.spawn
        self._sync_rect()
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = True
        self.coyote = COYOTE_FRAMES
        self.standing_on = self.platforms[0] if self.platforms else None
        if self.level == 3:
            self.message = f"Lava burns hard (−{dmg}). Hearts: {self.hearts}."
        else:
            self.message = f"Ouch! Hearts: {self.hearts}."

    def draw_cloud(self, x, y, w, h):
        t = self.theme
        pygame.draw.ellipse(self.screen, t["cloud"], (int(x), y, w, h))
        pygame.draw.ellipse(self.screen, t["cloud"], (int(x) + w // 3, y - h // 3, w // 2, h))
        pygame.draw.ellipse(self.screen, t["cloud"], (int(x) + w // 2, y, w // 2, int(h * 0.9)))
        pygame.draw.ellipse(self.screen, t["cloud_edge"], (int(x), y, w, h), 1)

    def draw_hazard(self):
        t = self.theme
        pygame.draw.rect(self.screen, t["hazard"], (0, WATER_Y, WIDTH, HEIGHT - WATER_Y))
        pygame.draw.rect(self.screen, t["hazard_deep"], (0, WATER_Y + 24, WIDTH, HEIGHT - WATER_Y - 24))
        for x in range(0, WIDTH, 18):
            pygame.draw.arc(self.screen, t["hazard_foam"], (x, WATER_Y - 4, 18, 10), 3.14, 6.28, 2)

    def draw_goal(self):
        dx, dy = 720, 72
        color = (120, 78, 48) if self.level == 1 else ((255, 230, 160) if self.level == 2 else (40, 20, 25))
        pygame.draw.ellipse(self.screen, color, (dx, dy + 8, 28, 14))
        pygame.draw.circle(self.screen, color, (dx + 26, dy + 10), 7)
        if self.level == 2:
            pygame.draw.ellipse(self.screen, (255, 220, 100), (dx + 18, dy - 2, 16, 6), 2)
        elif self.level == 3:
            pygame.draw.circle(self.screen, (255, 80, 40), (dx + 26, dy + 8), 2)

    def draw_hud(self):
        t = self.theme
        for i in range(max(self.hearts, MAX_HEARTS)):
            if i >= self.hearts and i >= MAX_HEARTS:
                break
            hx = 16 + i * 26
            color = HEART_COLOR if i < self.hearts else (120, 120, 130)
            pygame.draw.circle(self.screen, color, (hx + 5, 18), 5)
            pygame.draw.circle(self.screen, color, (hx + 13, 18), 5)
            pygame.draw.polygon(self.screen, color, [(hx, 20), (hx + 18, 20), (hx + 9, 30)])

        panel = pygame.Rect(16, 40, 168, 72)
        pygame.draw.rect(self.screen, (255, 255, 255) if self.level < 3 else (40, 20, 25), panel, border_radius=8)
        pygame.draw.rect(self.screen, t["accent"], panel, 2, border_radius=8)
        text_c = t["text"]
        self.screen.blit(self.small.render(f"Level {self.level}/3  {t['name']}", True, text_c), (28, 46))
        self.screen.blit(self.small.render(f"Coins  {self.money}", True, COIN_COLOR), (28, 64))
        self.screen.blit(self.small.render(f"Spells {self.spells}  (F)", True, SPELL_COLOR), (28, 82))

        if self.freeze_timer > 0:
            label = self.small.render("FROST ACTIVE", True, SPELL_COLOR)
            box = pygame.Rect(WIDTH // 2 - 60, 72, 120, 22)
            pygame.draw.rect(self.screen, (255, 255, 255), box, border_radius=6)
            self.screen.blit(label, (box.centerx - label.get_width() // 2, box.y + 2))

    def draw(self):
        self.tick += 1
        t = self.theme
        self.screen.blit(self.sky, (0, 0))

        for cloud in self.clouds:
            cloud["x"] += cloud["speed"] * (1.2 if self.level == 3 else 1.0)
            if cloud["x"] > WIDTH + 30:
                cloud["x"] = -cloud["w"]
            self.draw_cloud(cloud["x"], cloud["y"], cloud["w"], cloud["h"])

        title = self.font.render("Spring Crack", True, t["accent"])
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 6))
        sub = self.small.render(t["subtitle"], True, t["text"])
        self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 34))

        for p in self.platforms:
            p.draw(self.screen, t)

        self.draw_goal()

        for item in self.pickups:
            item.draw(self.screen, self.tick)

        draw_hero(
            self.screen,
            self.player,
            facing_right=self.facing_right,
            on_ground=self.on_ground,
            vel_y=self.vel_y,
            tier=t["hero_tier"],
        )

        self.draw_hazard()
        self.draw_hud()

        msg = self.small.render(self.message, True, t["text"])
        plate = pygame.Rect(WIDTH // 2 - msg.get_width() // 2 - 10, HEIGHT - 92, msg.get_width() + 20, 26)
        bg = (255, 255, 255) if self.level < 3 else (50, 25, 28)
        pygame.draw.rect(self.screen, bg, plate, border_radius=8)
        pygame.draw.rect(self.screen, t["accent"], plate, 1, border_radius=8)
        self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT - 88))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            running = self.handle_input()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
