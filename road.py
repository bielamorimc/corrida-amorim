"""Scrolling road renderer."""
import pygame

from settings import (
    COLOR_ASPHALT,
    COLOR_ASPHALT_DARK,
    COLOR_EDGE,
    COLOR_GRASS,
    COLOR_GRASS_DARK,
    COLOR_LINE,
    DASH_GAP,
    DASH_LENGTH,
    HEIGHT,
    LANE_COUNT,
    LANE_WIDTH,
    ROAD_LEFT,
    ROAD_RIGHT,
    WIDTH,
)


class Road:
    def __init__(self) -> None:
        self.scroll_y = 0.0
        self.dash_period = DASH_LENGTH + DASH_GAP

    def update(self, scroll_speed: float) -> None:
        self.scroll_y = (self.scroll_y + scroll_speed) % self.dash_period

    def draw(self, surface: pygame.Surface) -> None:
        # Grass sides: vertical two-tone stripes.
        pygame.draw.rect(surface, COLOR_GRASS, (0, 0, ROAD_LEFT, HEIGHT))
        pygame.draw.rect(surface, COLOR_GRASS, (ROAD_RIGHT, 0, WIDTH - ROAD_RIGHT, HEIGHT))
        stripe_h = 40
        offset = int(self.scroll_y * 2) % (stripe_h * 2)
        for y in range(-stripe_h * 2, HEIGHT + stripe_h * 2, stripe_h * 2):
            pygame.draw.rect(surface, COLOR_GRASS_DARK, (0, y + offset, ROAD_LEFT, stripe_h))
            pygame.draw.rect(surface, COLOR_GRASS_DARK,
                             (ROAD_RIGHT, y + offset, WIDTH - ROAD_RIGHT, stripe_h))

        # Asphalt.
        pygame.draw.rect(surface, COLOR_ASPHALT, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))
        # Subtle alternating asphalt bands for motion feel.
        band_h = 80
        band_off = int(self.scroll_y * 4) % (band_h * 2)
        for y in range(-band_h * 2, HEIGHT + band_h * 2, band_h * 2):
            pygame.draw.rect(surface, COLOR_ASPHALT_DARK,
                             (ROAD_LEFT, y + band_off, ROAD_RIGHT - ROAD_LEFT, band_h))

        # Solid edges.
        pygame.draw.rect(surface, COLOR_EDGE, (ROAD_LEFT - 4, 0, 4, HEIGHT))
        pygame.draw.rect(surface, COLOR_EDGE, (ROAD_RIGHT, 0, 4, HEIGHT))

        # Dashed lane dividers (between lanes, not edges).
        for i in range(1, LANE_COUNT):
            x = int(ROAD_LEFT + LANE_WIDTH * i) - 3
            y = -self.dash_period + self.scroll_y
            while y < HEIGHT:
                pygame.draw.rect(surface, COLOR_LINE, (x, int(y), 6, DASH_LENGTH))
                y += self.dash_period
