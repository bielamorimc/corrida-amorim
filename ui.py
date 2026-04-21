"""UI helpers: fonts, typewriter text, HUD, menu drawing."""
from __future__ import annotations

import pygame

from settings import (
    COLOR_ACCENT,
    COLOR_COIN_GOLD,
    COLOR_COIN_GOLD_DARK,
    COLOR_COIN_SHINE,
    COLOR_DANGER,
    COLOR_HUD_BG,
    COLOR_HUD_TEXT,
    COLOR_MENU_BG_BOTTOM,
    COLOR_MENU_BG_TOP,
    FONTS_DIR,
    HEIGHT,
    WIDTH,
)


_FONT_CACHE: dict[tuple[str, int, bool], pygame.font.Font] = {}


def get_font(size: int, bold: bool = False, family: str | None = None) -> pygame.font.Font:
    key = (family or "", size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    font: pygame.font.Font | None = None
    if family:
        path = FONTS_DIR / family
        if path.exists():
            try:
                font = pygame.font.Font(str(path), size)
            except pygame.error:
                font = None
    if font is None:
        sys_name = "arialblack" if bold else "arial"
        font = pygame.font.SysFont(sys_name, size, bold=bold)
    _FONT_CACHE[key] = font
    return font


def draw_vertical_gradient(surface: pygame.Surface, top: tuple[int, int, int],
                           bottom: tuple[int, int, int]) -> None:
    h = surface.get_height()
    w = surface.get_width()
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (w, y))


def draw_menu_background(surface: pygame.Surface, t_seconds: float) -> None:
    draw_vertical_gradient(surface, COLOR_MENU_BG_TOP, COLOR_MENU_BG_BOTTOM)
    # Scrolling diagonal speed streaks.
    streak_color = (255, 255, 255, 28)
    streak_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    spacing = 36
    offset = int((t_seconds * 220) % spacing)
    for i in range(-HEIGHT, WIDTH + HEIGHT, spacing):
        x = i + offset
        pygame.draw.line(streak_surf, streak_color, (x, 0), (x - HEIGHT, HEIGHT), 2)
    surface.blit(streak_surf, (0, 0))


class Typewriter:
    """Renders multi-line text one character at a time."""

    def __init__(self, lines: list[str], chars_per_second: float = 38.0) -> None:
        self.lines = lines
        self.cps = chars_per_second
        self.elapsed = 0.0
        self.total_chars = sum(len(line) for line in lines)
        self._finished_override = False

    @property
    def revealed(self) -> int:
        return min(self.total_chars, int(self.elapsed * self.cps))

    @property
    def finished(self) -> bool:
        return self._finished_override or self.revealed >= self.total_chars

    def update(self, dt: float) -> None:
        self.elapsed += dt

    def skip(self) -> None:
        self._finished_override = True

    def draw(self, surface: pygame.Surface, font: pygame.font.Font,
             top_y: int, color=COLOR_HUD_TEXT) -> None:
        revealed = self.total_chars if self._finished_override else self.revealed
        y = top_y
        consumed = 0
        for line in self.lines:
            if consumed >= revealed and line:
                break
            visible_count = max(0, min(len(line), revealed - consumed))
            visible = line[:visible_count]
            if visible or not line:
                text_surf = font.render(visible, True, color)
                rect = text_surf.get_rect(center=(WIDTH // 2, y))
                surface.blit(text_surf, rect)
            y += font.get_linesize() + 4
            consumed += len(line)


def draw_coin_icon(surface: pygame.Surface, center: tuple[int, int],
                   radius: int = 9) -> None:
    cx, cy = center
    pygame.draw.circle(surface, COLOR_COIN_GOLD_DARK, (cx, cy), radius + 1)
    pygame.draw.circle(surface, COLOR_COIN_GOLD, (cx, cy), radius)
    pygame.draw.ellipse(
        surface,
        COLOR_COIN_SHINE,
        pygame.Rect(cx - radius // 2, cy - radius // 2 - 1, radius, max(2, radius - 1)),
    )


def draw_car_preview(surface: pygame.Surface, center: tuple[int, int],
                     body: tuple[int, int, int], shadow: tuple[int, int, int],
                     scale: float = 2.0) -> None:
    from entities import _draw_car_body
    from settings import CAR_HEIGHT, CAR_WIDTH

    w = int(CAR_WIDTH * scale)
    h = int(CAR_HEIGHT * scale)
    rect = pygame.Rect(0, 0, w, h)
    rect.center = center
    _draw_car_body(surface, rect, body, shadow, facing_up=True)


def draw_stat_bar(surface: pygame.Surface, rect: pygame.Rect, label: str,
                  fraction: float) -> None:
    font = get_font(14, bold=True)
    fraction = max(0.0, min(1.0, fraction))
    label_surf = font.render(label, True, COLOR_HUD_TEXT)
    surface.blit(label_surf, (rect.x, rect.y - 4))
    bar_rect = pygame.Rect(rect.x + 90, rect.y, rect.width - 90, rect.height)
    pygame.draw.rect(surface, (30, 30, 40), bar_rect, border_radius=4)
    fill = bar_rect.copy()
    fill.width = int(bar_rect.width * fraction)
    if fill.width > 0:
        pygame.draw.rect(surface, COLOR_ACCENT, fill, border_radius=4)
    pygame.draw.rect(surface, COLOR_HUD_TEXT, bar_rect, width=1, border_radius=4)


def draw_hud(surface: pygame.Surface, score: int, high: int, coins: int,
             speed: float, difficulty: float, muted: bool) -> None:
    font = get_font(20, bold=True)
    small = get_font(14, bold=True)

    # Top bar.
    bar = pygame.Surface((WIDTH, 56), pygame.SRCALPHA)
    bar.fill(COLOR_HUD_BG)
    surface.blit(bar, (0, 0))

    score_surf = font.render(f"PONTOS  {score:05d}", True, COLOR_HUD_TEXT)
    surface.blit(score_surf, (14, 8))
    high_surf = small.render(f"RECORDE  {high:05d}", True, COLOR_ACCENT)
    surface.blit(high_surf, (14, 32))

    speed_surf = font.render(f"{int(speed * 12)} KM/H", True, COLOR_HUD_TEXT)
    surface.blit(speed_surf, speed_surf.get_rect(topright=(WIDTH - 14, 8)))
    diff_surf = small.render(f"NIVEL  {difficulty:.1f}x", True, COLOR_ACCENT)
    surface.blit(diff_surf, diff_surf.get_rect(topright=(WIDTH - 14, 32)))

    # Coins pill, centered below the top bar.
    coin_text = f"{coins:03d}"
    coin_font = get_font(18, bold=True)
    text_surf = coin_font.render(coin_text, True, COLOR_ACCENT)
    pill_w = text_surf.get_width() + 44
    pill_rect = pygame.Rect(0, 0, pill_w, 26)
    pill_rect.midtop = (WIDTH // 2, 60)
    pill_bg = pygame.Surface(pill_rect.size, pygame.SRCALPHA)
    pill_bg.fill((0, 0, 0, 160))
    surface.blit(pill_bg, pill_rect.topleft)
    draw_coin_icon(surface, (pill_rect.left + 16, pill_rect.centery), radius=9)
    surface.blit(text_surf, text_surf.get_rect(midleft=(pill_rect.left + 30, pill_rect.centery)))

    if muted:
        mute_surf = small.render("MUDO", True, COLOR_DANGER)
        surface.blit(mute_surf, mute_surf.get_rect(midbottom=(WIDTH // 2, 52)))


def draw_center_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
                     y: int, color=COLOR_HUD_TEXT) -> pygame.Rect:
    text_surf = font.render(text, True, color)
    rect = text_surf.get_rect(center=(WIDTH // 2, y))
    surface.blit(text_surf, rect)
    return rect


def draw_menu_item(surface: pygame.Surface, text: str, y: int, selected: bool) -> None:
    font = get_font(28, bold=True)
    color = COLOR_ACCENT if selected else COLOR_HUD_TEXT
    rect = draw_center_text(surface, text, font, y, color)
    if selected:
        marker = font.render(">", True, COLOR_ACCENT)
        surface.blit(marker, marker.get_rect(midright=(rect.left - 16, y)))
        marker2 = font.render("<", True, COLOR_ACCENT)
        surface.blit(marker2, marker2.get_rect(midleft=(rect.right + 16, y)))
