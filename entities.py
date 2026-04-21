"""Player car, enemy cars, coins, and their spawners."""
from __future__ import annotations

import math
import random

import pygame

from cars import Car, get_car
from settings import (
    CAR_HEIGHT,
    CAR_WIDTH,
    COIN_BASE_COOLDOWN,
    COIN_GAP_SAME_LANE,
    COIN_MIN_COOLDOWN,
    COIN_PICKUP_INFLATE,
    COIN_RADIUS,
    COIN_TIERS,
    COLOR_COIN_SHINE,
    COLOR_ENEMY_PALETTE,
    COLOR_HEADLIGHT,
    COLOR_TAILLIGHT,
    COLOR_WINDOW,
    ENEMY_SPEED_JITTER,
    HEIGHT,
    LANE_COUNT,
    LANES,
    LANE_SNAP_SPEED,
    MIN_SPAWN_GAP,
    PLAYER_Y,
    SPAWN_BASE_COOLDOWN,
    SPAWN_MIN_COOLDOWN,
)


def _draw_car_body(surface: pygame.Surface, rect: pygame.Rect,
                   body: tuple[int, int, int], shadow: tuple[int, int, int],
                   facing_up: bool) -> None:
    # Shadow.
    shadow_rect = rect.move(2, 3)
    pygame.draw.rect(surface, (0, 0, 0), shadow_rect, border_radius=10)
    # Body.
    pygame.draw.rect(surface, body, rect, border_radius=10)
    # Side shading.
    pygame.draw.rect(surface, shadow, rect, width=3, border_radius=10)

    # Windshield + rear window.
    w = rect.width
    h = rect.height
    win_w = int(w * 0.68)
    win_h = int(h * 0.22)
    win_x = rect.x + (w - win_w) // 2
    front_y = rect.y + int(h * 0.18)
    back_y = rect.y + int(h * 0.60)
    pygame.draw.rect(surface, COLOR_WINDOW, (win_x, front_y, win_w, win_h), border_radius=4)
    pygame.draw.rect(surface, COLOR_WINDOW, (win_x, back_y, win_w, win_h), border_radius=4)

    # Headlights / taillights.
    light_w = 10
    light_h = 5
    top_lights_y = rect.y + 4
    bottom_lights_y = rect.bottom - 4 - light_h
    if facing_up:
        pygame.draw.rect(surface, COLOR_HEADLIGHT,
                         (rect.x + 6, top_lights_y, light_w, light_h))
        pygame.draw.rect(surface, COLOR_HEADLIGHT,
                         (rect.right - 6 - light_w, top_lights_y, light_w, light_h))
        pygame.draw.rect(surface, COLOR_TAILLIGHT,
                         (rect.x + 6, bottom_lights_y, light_w, light_h))
        pygame.draw.rect(surface, COLOR_TAILLIGHT,
                         (rect.right - 6 - light_w, bottom_lights_y, light_w, light_h))
    else:
        pygame.draw.rect(surface, COLOR_TAILLIGHT,
                         (rect.x + 6, top_lights_y, light_w, light_h))
        pygame.draw.rect(surface, COLOR_TAILLIGHT,
                         (rect.right - 6 - light_w, top_lights_y, light_w, light_h))
        pygame.draw.rect(surface, COLOR_HEADLIGHT,
                         (rect.x + 6, bottom_lights_y, light_w, light_h))
        pygame.draw.rect(surface, COLOR_HEADLIGHT,
                         (rect.right - 6 - light_w, bottom_lights_y, light_w, light_h))

    # Wheels as dark stripes on sides.
    wheel_w = 6
    wheel_h = 18
    for wy_ratio in (0.22, 0.70):
        wy = rect.y + int(h * wy_ratio)
        pygame.draw.rect(surface, (20, 20, 20), (rect.x - 2, wy, wheel_w, wheel_h),
                         border_radius=2)
        pygame.draw.rect(surface, (20, 20, 20),
                         (rect.right - wheel_w + 2, wy, wheel_w, wheel_h),
                         border_radius=2)


class PlayerCar:
    def __init__(self, car: Car | None = None) -> None:
        self.car = car if car is not None else get_car("gabriel")
        self.lane = 1
        self.x = float(LANES[self.lane])
        self.y = PLAYER_Y
        self.rect = pygame.Rect(0, 0, CAR_WIDTH, CAR_HEIGHT)
        self._snap_speed = LANE_SNAP_SPEED * self.car.handling
        self._sync_rect()

    def _sync_rect(self) -> None:
        self.rect.center = (int(self.x), int(self.y))

    def move_left(self) -> None:
        if self.lane > 0:
            self.lane -= 1

    def move_right(self) -> None:
        if self.lane < LANE_COUNT - 1:
            self.lane += 1

    def reset(self) -> None:
        self.lane = 1
        self.x = float(LANES[self.lane])
        self._sync_rect()

    def update(self) -> None:
        target = LANES[self.lane]
        snap = self._snap_speed
        if abs(self.x - target) < snap:
            self.x = float(target)
        elif self.x < target:
            self.x += snap
        else:
            self.x -= snap
        self._sync_rect()

    def draw(self, surface: pygame.Surface) -> None:
        _draw_car_body(surface, self.rect, self.car.body, self.car.shadow, facing_up=True)


class EnemyCar:
    __slots__ = ("lane", "x", "y", "speed", "body", "shadow", "rect")

    def __init__(self, lane: int, spawn_y: float, speed: float) -> None:
        self.lane = lane
        self.x = float(LANES[lane])
        self.y = spawn_y
        self.speed = speed
        self.body, self.shadow = random.choice(COLOR_ENEMY_PALETTE)
        self.rect = pygame.Rect(0, 0, CAR_WIDTH, CAR_HEIGHT)
        self.rect.center = (int(self.x), int(self.y))

    def update(self, scroll_speed: float) -> None:
        self.y += self.speed + scroll_speed
        self.rect.center = (int(self.x), int(self.y))

    def off_screen(self) -> bool:
        return self.y - CAR_HEIGHT / 2 > HEIGHT + 20

    def draw(self, surface: pygame.Surface) -> None:
        _draw_car_body(surface, self.rect, self.body, self.shadow, facing_up=False)


class Spawner:
    # A lane is considered "blocking" the player if its topmost car is above
    # this y — i.e. still near the top of the screen.
    BLOCK_THRESHOLD_Y = 280

    def __init__(self) -> None:
        self.cooldown = 0.0
        self.enemies: list[EnemyCar] = []

    def reset(self) -> None:
        self.cooldown = 0.0
        self.enemies.clear()

    def update(self, dt: float, scroll_speed: float, difficulty: float) -> None:
        self.cooldown -= dt
        if self.cooldown <= 0:
            self._try_spawn(difficulty)
            self.cooldown = max(SPAWN_MIN_COOLDOWN, SPAWN_BASE_COOLDOWN / difficulty)

        for enemy in self.enemies:
            enemy.update(scroll_speed)
        self.enemies = [e for e in self.enemies if not e.off_screen()]

    def topmost_y_per_lane(self) -> list[float]:
        tops = [float("inf")] * LANE_COUNT
        for e in self.enemies:
            if e.y < tops[e.lane]:
                tops[e.lane] = e.y
        return tops

    def _try_spawn(self, difficulty: float) -> None:
        spawn_y = -CAR_HEIGHT
        tops = self.topmost_y_per_lane()

        # Only spawn in lanes whose topmost car is far enough below spawn point.
        candidates = [
            lane for lane in range(LANE_COUNT)
            if tops[lane] - spawn_y > MIN_SPAWN_GAP
        ]
        if not candidates:
            return

        # Reachability: never block every lane near the top. A lane is
        # "blocked" if its topmost car is above BLOCK_THRESHOLD_Y.
        def would_leave_open_lane(pick: int) -> bool:
            for lane in range(LANE_COUNT):
                if lane == pick:
                    continue
                if tops[lane] > self.BLOCK_THRESHOLD_Y:
                    return True
            return False

        safe = [lane for lane in candidates if would_leave_open_lane(lane)]
        if not safe:
            return
        lane = random.choice(safe)

        low, high = ENEMY_SPEED_JITTER
        speed = random.uniform(low, high) * min(difficulty, 2.0)
        self.enemies.append(EnemyCar(lane, spawn_y, speed))

    def collides_with(self, player_rect: pygame.Rect) -> bool:
        # Tight collision: shrink both rects slightly for fairness.
        shrink = 6
        pr = player_rect.inflate(-shrink * 2, -shrink * 2)
        for enemy in self.enemies:
            er = enemy.rect.inflate(-shrink * 2, -shrink * 2)
            if pr.colliderect(er):
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        for enemy in self.enemies:
            enemy.draw(surface)


# --- Coins ----------------------------------------------------------------


class Coin:
    __slots__ = ("lane", "x", "y", "value", "body", "dark", "phase", "rect")

    def __init__(self, lane: int, spawn_y: float, value: int,
                 body: tuple[int, int, int], dark: tuple[int, int, int]) -> None:
        self.lane = lane
        self.x = float(LANES[lane])
        self.y = spawn_y
        self.value = value
        self.body = body
        self.dark = dark
        self.phase = random.uniform(0, math.tau)
        r = COIN_RADIUS
        self.rect = pygame.Rect(int(self.x - r), int(self.y - r), r * 2, r * 2)

    def update(self, scroll_speed: float, dt: float) -> None:
        self.y += scroll_speed
        self.phase += dt * 6.0
        self.rect.center = (int(self.x), int(self.y))

    def off_screen(self) -> bool:
        return self.y - COIN_RADIUS > HEIGHT + 20

    def draw(self, surface: pygame.Surface) -> None:
        # Pulse squish via ellipse width (gives a spinning-coin feel).
        squish = 0.55 + 0.45 * abs(math.sin(self.phase))
        cx, cy = int(self.x), int(self.y)
        width = max(4, int(COIN_RADIUS * 2 * squish))
        height = COIN_RADIUS * 2
        ring = pygame.Rect(cx - width // 2 - 2, cy - height // 2 - 2, width + 4, height + 4)
        body = pygame.Rect(cx - width // 2, cy - height // 2, width, height)
        pygame.draw.ellipse(surface, self.dark, ring)
        pygame.draw.ellipse(surface, self.body, body)
        # Inner shine highlight.
        shine_w = max(2, width // 3)
        shine_h = max(2, height // 2)
        shine = pygame.Rect(cx - shine_w // 2, cy - shine_h // 2 - 2, shine_w, shine_h)
        pygame.draw.ellipse(surface, COLOR_COIN_SHINE, shine)


class CoinSpawner:
    def __init__(self) -> None:
        self.cooldown = 0.3
        self.coins: list[Coin] = []

    def reset(self) -> None:
        self.cooldown = 0.3
        self.coins.clear()

    def update(self, dt: float, scroll_speed: float, difficulty: float,
               enemy_tops_per_lane: list[float]) -> None:
        self.cooldown -= dt
        if self.cooldown <= 0:
            self._try_spawn(enemy_tops_per_lane)
            base = COIN_BASE_COOLDOWN / max(1.0, math.sqrt(difficulty))
            self.cooldown = max(COIN_MIN_COOLDOWN, base)

        for coin in self.coins:
            coin.update(scroll_speed, dt)
        self.coins = [c for c in self.coins if not c.off_screen()]

    def _topmost_coin_per_lane(self) -> list[float]:
        tops = [float("inf")] * LANE_COUNT
        for c in self.coins:
            if c.y < tops[c.lane]:
                tops[c.lane] = c.y
        return tops

    def _try_spawn(self, enemy_tops_per_lane: list[float]) -> None:
        spawn_y = -COIN_RADIUS
        coin_tops = self._topmost_coin_per_lane()
        candidates: list[int] = []
        for lane in range(LANE_COUNT):
            # Respect same-lane coin spacing.
            if coin_tops[lane] - spawn_y <= COIN_GAP_SAME_LANE:
                continue
            # Don't spawn directly on top of an enemy still near the top.
            if enemy_tops_per_lane[lane] - spawn_y < 70:
                continue
            candidates.append(lane)
        if not candidates:
            return
        lane = random.choice(candidates)
        value, body, dark = _choose_coin_tier()
        self.coins.append(Coin(lane, spawn_y, value, body, dark))

    def collect(self, player_rect: pygame.Rect) -> int:
        if not self.coins:
            return 0
        inflated = player_rect.inflate(COIN_PICKUP_INFLATE * 2, COIN_PICKUP_INFLATE * 2)
        gained = 0
        remaining: list[Coin] = []
        for coin in self.coins:
            if inflated.colliderect(coin.rect):
                gained += coin.value
            else:
                remaining.append(coin)
        self.coins = remaining
        return gained

    def draw(self, surface: pygame.Surface) -> None:
        for coin in self.coins:
            coin.draw(surface)


def _choose_coin_tier() -> tuple[int, tuple[int, int, int], tuple[int, int, int]]:
    total = sum(weight for _, weight, _, _ in COIN_TIERS)
    pick = random.uniform(0, total)
    running = 0.0
    for value, weight, body, dark in COIN_TIERS:
        running += weight
        if pick <= running:
            return value, body, dark
    value, _, body, dark = COIN_TIERS[0]
    return value, body, dark
