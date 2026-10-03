"""Hero forms: Earth traveler → Heaven ascendant → Hell champion."""

import pygame


TIERS = {
    1: {  # Earth
        "skin": (232, 196, 168),
        "hair": (78, 52, 40),
        "coat": (176, 64, 56),
        "scarf": (212, 148, 72),
        "pants": (72, 78, 96),
        "boots": (56, 44, 36),
        "accent": (92, 70, 52),
    },
    2: {  # Heaven — white/gold + halo
        "skin": (255, 230, 210),
        "hair": (255, 230, 140),
        "coat": (250, 250, 255),
        "scarf": (255, 210, 90),
        "pants": (220, 225, 245),
        "boots": (230, 200, 120),
        "accent": (255, 220, 120),
    },
    3: {  # Hell — dark ember armor
        "skin": (210, 160, 140),
        "hair": (30, 20, 20),
        "coat": (90, 25, 30),
        "scarf": (220, 80, 40),
        "pants": (40, 25, 30),
        "boots": (25, 15, 15),
        "accent": (255, 100, 40),
    },
}


def draw_hero(surface, rect, facing_right=True, on_ground=True, vel_y=0, tier=1):
    colors = TIERS.get(tier, TIERS[1])
    cx = rect.centerx
    bottom = rect.bottom
    stretch = 0 if on_ground else (-2 if vel_y < 0 else 2)
    y = bottom + stretch

    shadow = pygame.Surface((26, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (20, 20, 30, 70), shadow.get_rect())
    surface.blit(shadow, (cx - 13, bottom - 2))

    if tier == 2:
        pygame.draw.ellipse(surface, colors["accent"], (cx - 12, y - 58, 24, 10), 2)
    elif tier == 3:
        pygame.draw.polygon(
            surface, colors["accent"], [(cx - 10, y - 48), (cx - 14, y - 58), (cx - 4, y - 50)]
        )
        pygame.draw.polygon(
            surface, colors["accent"], [(cx + 10, y - 48), (cx + 14, y - 58), (cx + 4, y - 50)]
        )

    pygame.draw.rect(surface, colors["boots"], (cx - 8, y - 8, 7, 6), border_radius=2)
    pygame.draw.rect(surface, colors["boots"], (cx + 1, y - 8, 7, 6), border_radius=2)
    pygame.draw.rect(surface, colors["pants"], (cx - 7, y - 16, 6, 10), border_radius=2)
    pygame.draw.rect(surface, colors["pants"], (cx + 1, y - 16, 6, 10), border_radius=2)

    pygame.draw.rect(surface, colors["coat"], (cx - 10, y - 30, 20, 16), border_radius=4)
    pygame.draw.rect(surface, colors["scarf"], (cx - 9, y - 32, 18, 5), border_radius=2)
    if facing_right:
        pygame.draw.rect(surface, colors["scarf"], (cx + 7, y - 28, 5, 10), border_radius=2)
    else:
        pygame.draw.rect(surface, colors["scarf"], (cx - 12, y - 28, 5, 10), border_radius=2)

    if tier == 2:
        pygame.draw.line(surface, (255, 240, 180), (cx - 8, y - 28), (cx - 8, y - 16), 2)
    elif tier == 3:
        pygame.draw.line(surface, colors["accent"], (cx + 8, y - 28), (cx + 8, y - 14), 2)

    pygame.draw.circle(surface, colors["skin"], (cx, y - 38), 8)
    pygame.draw.ellipse(surface, colors["hair"], (cx - 8, y - 48, 16, 11))
    pygame.draw.rect(surface, colors["coat"], (cx - 8, y - 42, 16, 4), border_radius=2)

    eye = (40, 32, 28) if tier != 3 else (255, 120, 60)
    if facing_right:
        pygame.draw.circle(surface, eye, (cx + 3, y - 38), 1)
    else:
        pygame.draw.circle(surface, eye, (cx - 3, y - 38), 1)

    if facing_right:
        pygame.draw.rect(surface, colors["accent"], (cx - 12, y - 28, 7, 10), border_radius=2)
    else:
        pygame.draw.rect(surface, colors["accent"], (cx + 5, y - 28, 7, 10), border_radius=2)

    if tier >= 2:
        pygame.draw.circle(surface, colors["accent"], (cx + (10 if facing_right else -10), y - 34), 3)
