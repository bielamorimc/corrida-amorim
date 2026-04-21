"""State machine: Menu, Story, Race, Pause, GameOver."""
from __future__ import annotations

import math

import pygame

from audio import SoundManager
from cars import CARS, get_car
from entities import CoinSpawner, PlayerCar, Spawner
from road import Road
from settings import (
    BASE_SCROLL,
    COLOR_ACCENT,
    COLOR_DANGER,
    COLOR_HUD_BG,
    COLOR_HUD_TEXT,
    DIFFICULTY_RAMP_SECONDS,
    HEIGHT,
    MAX_DIFFICULTY,
    SCORE_PER_PIXEL,
    STORY_LINES,
    WIDTH,
)
from storage import (
    add_coins,
    load_profile,
    purchase_car,
    save_profile,
    set_selected,
)
from ui import (
    Typewriter,
    draw_car_preview,
    draw_center_text,
    draw_coin_icon,
    draw_hud,
    draw_menu_background,
    draw_menu_item,
    draw_stat_bar,
    get_font,
)


class State:
    """Base class: returns the next State, or None to quit."""

    def handle_events(self, events: list[pygame.event.Event]) -> "State | None":
        return self

    def update(self, dt: float) -> "State | None":
        return self

    def draw(self, surface: pygame.Surface) -> None:
        pass


# --- Menu ---------------------------------------------------------------

class MenuState(State):
    OPTIONS = ["COMECAR", "GARAGEM", "RECORDE", "SAIR"]

    def __init__(self, audio: SoundManager) -> None:
        self.audio = audio
        self.audio.stop_engine()
        self.selected = 0
        self.time = 0.0
        self.profile = load_profile()

    def handle_events(self, events: list[pygame.event.Event]) -> "State | None":
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected = (self.selected - 1) % len(self.OPTIONS)
                    self.audio.play("click")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected = (self.selected + 1) % len(self.OPTIONS)
                    self.audio.play("click")
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    return self._activate()
                elif event.key == pygame.K_m:
                    self.audio.toggle_mute()
                elif event.key == pygame.K_ESCAPE:
                    return None
        return self

    def _activate(self) -> "State | None":
        self.audio.play("click")
        if self.selected == 0:
            return StoryState(self.audio)
        if self.selected == 1:
            return GarageState(self.audio)
        if self.selected == 2:
            return HighscoreState(self.audio, int(self.profile.get("best", 0)))
        return None

    def update(self, dt: float) -> "State | None":
        self.time += dt
        return self

    def draw(self, surface: pygame.Surface) -> None:
        draw_menu_background(surface, self.time)

        title_font = get_font(96, bold=True)
        subtitle_font = get_font(26, bold=True)
        prompt_font = get_font(18, bold=True)

        # Title with soft shadow.
        shadow = title_font.render("AMORIM", True, (0, 0, 0))
        surface.blit(shadow, shadow.get_rect(center=(WIDTH // 2 + 4, 140 + 4)))
        title = title_font.render("AMORIM", True, COLOR_ACCENT)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 140)))

        draw_center_text(surface, "C O R R I D A S", subtitle_font, 200, COLOR_HUD_TEXT)

        # Current car + pilot banner.
        car = get_car(self.profile.get("selected", "gabriel"))
        name_font = get_font(18, bold=True)
        draw_center_text(surface, "Piloto: GABRIEL AMORIM", name_font, 240, COLOR_HUD_TEXT)
        draw_center_text(surface, f"Carro: {car.name}", name_font, 264, COLOR_ACCENT)

        # Menu items.
        base_y = 340
        for i, option in enumerate(self.OPTIONS):
            draw_menu_item(surface, option, base_y + i * 50, i == self.selected)

        # Blinking prompt.
        if int(self.time * 2) % 2 == 0:
            draw_center_text(
                surface,
                "ENTER confirma  .  M muta  .  ESC sai",
                prompt_font,
                HEIGHT - 40,
                COLOR_HUD_TEXT,
            )

        # Bottom corners: highscore + coin balance.
        corner_font = get_font(16, bold=True)
        hs_surf = corner_font.render(
            f"RECORDE  {int(self.profile.get('best', 0)):05d}", True, COLOR_ACCENT
        )
        surface.blit(hs_surf, (16, HEIGHT - 30))

        coins = int(self.profile.get("coins", 0))
        coin_label = corner_font.render(f"{coins}", True, COLOR_ACCENT)
        label_rect = coin_label.get_rect(bottomright=(WIDTH - 16, HEIGHT - 14))
        surface.blit(coin_label, label_rect)
        draw_coin_icon(surface, (label_rect.left - 14, label_rect.centery), radius=9)


# --- Highscore popup ---------------------------------------------------

class HighscoreState(State):
    def __init__(self, audio: SoundManager, highscore: int) -> None:
        self.audio = audio
        self.highscore = highscore
        self.time = 0.0

    def handle_events(self, events: list[pygame.event.Event]) -> "State | None":
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE,
                                 pygame.K_KP_ENTER):
                    self.audio.play("click")
                    return MenuState(self.audio)
        return self

    def update(self, dt: float) -> "State | None":
        self.time += dt
        return self

    def draw(self, surface: pygame.Surface) -> None:
        draw_menu_background(surface, self.time)
        draw_center_text(surface, "RECORDE ATUAL", get_font(40, bold=True), 240, COLOR_ACCENT)
        draw_center_text(surface, f"{self.highscore:05d}", get_font(90, bold=True),
                         360, COLOR_HUD_TEXT)
        draw_center_text(surface, "ENTER voltar", get_font(18, bold=True), HEIGHT - 60,
                         COLOR_HUD_TEXT)


# --- Story --------------------------------------------------------------

class StoryState(State):
    def __init__(self, audio: SoundManager) -> None:
        self.audio = audio
        self.typewriter = Typewriter(STORY_LINES, chars_per_second=42)
        self.hold_timer = 0.0

    def handle_events(self, events: list[pygame.event.Event]) -> "State | None":
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return MenuState(self.audio)
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                    if not self.typewriter.finished:
                        self.typewriter.skip()
                    else:
                        self.audio.play("countdown")
                        return RaceState(self.audio)
        return self

    def update(self, dt: float) -> "State | None":
        self.typewriter.update(dt)
        if self.typewriter.finished:
            self.hold_timer += dt
        return self

    def draw(self, surface: pygame.Surface) -> None:
        draw_menu_background(surface, self.hold_timer + 1.0)
        heading_font = get_font(30, bold=True)
        body_font = get_font(22, bold=True)
        draw_center_text(surface, "A LENDA AMORIM", heading_font, 100, COLOR_ACCENT)
        self.typewriter.draw(surface, body_font, 200)

        prompt = "ENTER continua" if self.typewriter.finished else "ENTER pular"
        draw_center_text(surface, prompt, get_font(18, bold=True), HEIGHT - 50, COLOR_HUD_TEXT)


# --- Race ---------------------------------------------------------------

class RaceState(State):
    def __init__(self, audio: SoundManager) -> None:
        self.audio = audio
        self.profile = load_profile()
        car = get_car(self.profile.get("selected", "gabriel"))
        self.road = Road()
        self.player = PlayerCar(car)
        self.spawner = Spawner()
        self.coin_spawner = CoinSpawner()
        self.elapsed = 0.0
        self.distance = 0.0
        self.score = 0
        self.coins_collected = 0
        self.highscore = int(self.profile.get("best", 0))
        self.speed_boost = 0.0  # from holding accelerate
        self.speed_brake = 0.0  # from holding brake
        self.audio.start_engine()

    @property
    def difficulty(self) -> float:
        return min(MAX_DIFFICULTY, 1.0 + self.elapsed / DIFFICULTY_RAMP_SECONDS)

    @property
    def scroll_speed(self) -> float:
        base = BASE_SCROLL * self.difficulty * self.player.car.top_speed
        return max(2.0, base + self.speed_boost - self.speed_brake)

    def handle_events(self, events: list[pygame.event.Event]) -> "State | None":
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.player.move_left()
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.player.move_right()
                elif event.key == pygame.K_p:
                    return PauseState(self.audio, self)
                elif event.key == pygame.K_ESCAPE:
                    return MenuState(self.audio)
                elif event.key == pygame.K_m:
                    self.audio.toggle_mute()
        return self

    def update(self, dt: float) -> "State | None":
        keys = pygame.key.get_pressed()
        self.speed_boost = 2.5 if (keys[pygame.K_UP] or keys[pygame.K_w]) else 0.0
        self.speed_brake = 2.0 if (keys[pygame.K_DOWN] or keys[pygame.K_s]) else 0.0

        self.elapsed += dt
        scroll = self.scroll_speed
        self.road.update(scroll)
        self.player.update()
        self.spawner.update(dt, scroll, self.difficulty)
        self.coin_spawner.update(dt, scroll, self.difficulty,
                                 self.spawner.topmost_y_per_lane())
        self.distance += scroll
        self.score = int(self.distance * SCORE_PER_PIXEL)

        gained = self.coin_spawner.collect(self.player.rect)
        if gained:
            self.coins_collected += gained
            self.audio.play("coin")

        self.audio.set_engine_intensity(
            (self.scroll_speed - BASE_SCROLL) / (BASE_SCROLL * MAX_DIFFICULTY)
        )

        if self.spawner.collides_with(self.player.rect):
            self.audio.play("crash")
            self.audio.stop_engine()
            new_record = self.score > self.highscore
            # Commit run rewards to profile.
            profile = load_profile()
            add_coins(profile, self.coins_collected)
            if new_record:
                profile["best"] = self.score
            save_profile(profile)
            return GameOverState(self.audio, self.score, self.highscore,
                                 self.coins_collected, new_record)
        return self

    def draw(self, surface: pygame.Surface) -> None:
        self.road.draw(surface)
        self.coin_spawner.draw(surface)
        self.spawner.draw(surface)
        self.player.draw(surface)
        draw_hud(surface, self.score, max(self.highscore, self.score),
                 self.coins_collected, self.scroll_speed, self.difficulty,
                 self.audio.muted)


# --- Pause --------------------------------------------------------------

class PauseState(State):
    def __init__(self, audio: SoundManager, race: RaceState) -> None:
        self.audio = audio
        self.race = race
        self.audio.stop_engine()
        self.time = 0.0

    def handle_events(self, events: list[pygame.event.Event]) -> "State | None":
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_RETURN:
                    self.audio.start_engine()
                    return self.race
                if event.key == pygame.K_ESCAPE:
                    return MenuState(self.audio)
                if event.key == pygame.K_m:
                    self.audio.toggle_mute()
        return self

    def update(self, dt: float) -> "State | None":
        self.time += dt
        return self

    def draw(self, surface: pygame.Surface) -> None:
        self.race.draw(surface)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        draw_center_text(surface, "PAUSADO", get_font(64, bold=True),
                         HEIGHT // 2 - 40, COLOR_ACCENT)
        blink = int(self.time * 2) % 2 == 0
        if blink:
            draw_center_text(surface, "P continua  .  ESC menu",
                             get_font(20, bold=True), HEIGHT // 2 + 30, COLOR_HUD_TEXT)


# --- Game Over ----------------------------------------------------------

class GameOverState(State):
    def __init__(self, audio: SoundManager, score: int, prev_high: int,
                 coins_collected: int, new_record: bool) -> None:
        self.audio = audio
        self.score = score
        self.displayed_high = max(prev_high, score)
        self.coins_collected = coins_collected
        self.new_record = new_record
        self.time = 0.0

    def handle_events(self, events: list[pygame.event.Event]) -> "State | None":
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                    self.audio.play("click")
                    return RaceState(self.audio)
                if event.key == pygame.K_ESCAPE:
                    return MenuState(self.audio)
                if event.key == pygame.K_m:
                    self.audio.toggle_mute()
        return self

    def update(self, dt: float) -> "State | None":
        self.time += dt
        return self

    def draw(self, surface: pygame.Surface) -> None:
        draw_menu_background(surface, self.time + 2.0)
        draw_center_text(surface, "CORRIDA ENCERRADA", get_font(36, bold=True),
                         130, COLOR_DANGER)
        draw_center_text(surface, "GABRIEL AMORIM", get_font(22, bold=True),
                         176, COLOR_HUD_TEXT)

        draw_center_text(surface, "PONTUACAO", get_font(22, bold=True),
                         250, COLOR_HUD_TEXT)
        draw_center_text(surface, f"{self.score:05d}", get_font(80, bold=True),
                         316, COLOR_ACCENT)

        # Coins earned this run.
        coin_label = get_font(22, bold=True).render(
            f"+ {self.coins_collected} MOEDAS", True, COLOR_ACCENT
        )
        lab_rect = coin_label.get_rect(center=(WIDTH // 2 + 14, 392))
        surface.blit(coin_label, lab_rect)
        draw_coin_icon(surface, (lab_rect.left - 18, lab_rect.centery), radius=11)

        if self.new_record and int(self.time * 3) % 2 == 0:
            draw_center_text(surface, "!!  NOVO RECORDE  !!",
                             get_font(26, bold=True), 450, COLOR_ACCENT)
        else:
            draw_center_text(surface, f"RECORDE  {self.displayed_high:05d}",
                             get_font(22, bold=True), 450, COLOR_HUD_TEXT)

        prompt_blink = int(self.time * 2) % 2 == 0
        if prompt_blink:
            draw_center_text(surface, "ENTER correr de novo  .  ESC menu",
                             get_font(18, bold=True), HEIGHT - 60, COLOR_HUD_TEXT)


# --- Garage (shop + car selection) --------------------------------------

class GarageState(State):
    FLASH_DURATION = 1.2

    def __init__(self, audio: SoundManager) -> None:
        self.audio = audio
        self.profile = load_profile()
        self.cars = CARS
        current = self.profile.get("selected", "gabriel")
        self.index = next(
            (i for i, c in enumerate(self.cars) if c.id == current), 0
        )
        self.time = 0.0
        self.flash_text = ""
        self.flash_color = COLOR_ACCENT
        self.flash_timer = 0.0

    def _flash(self, text: str, color: tuple[int, int, int]) -> None:
        self.flash_text = text
        self.flash_color = color
        self.flash_timer = self.FLASH_DURATION

    def _current_car(self):
        return self.cars[self.index]

    def handle_events(self, events: list[pygame.event.Event]) -> "State | None":
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.index = (self.index - 1) % len(self.cars)
                    self.audio.play("click")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.index = (self.index + 1) % len(self.cars)
                    self.audio.play("click")
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    self._activate_current()
                elif event.key == pygame.K_ESCAPE:
                    return MenuState(self.audio)
                elif event.key == pygame.K_m:
                    self.audio.toggle_mute()
        return self

    def _activate_current(self) -> None:
        car = self._current_car()
        owned = self.profile.get("owned", [])
        if car.id in owned:
            if self.profile.get("selected") == car.id:
                self._flash("JA SELECIONADO", COLOR_HUD_TEXT)
            else:
                set_selected(self.profile, car.id)
                save_profile(self.profile)
                self.audio.play("click")
                self._flash(f"{car.name.upper()} SELECIONADO", COLOR_ACCENT)
            return
        # Not owned: attempt purchase.
        if purchase_car(self.profile, car.id, car.price):
            save_profile(self.profile)
            self.audio.play("coin")
            self._flash("COMPRADO!", COLOR_ACCENT)
        else:
            self.audio.play("crash")
            self._flash("MOEDAS INSUFICIENTES", COLOR_DANGER)

    def update(self, dt: float) -> "State | None":
        self.time += dt
        if self.flash_timer > 0:
            self.flash_timer = max(0.0, self.flash_timer - dt)
        return self

    def draw(self, surface: pygame.Surface) -> None:
        draw_menu_background(surface, self.time)
        car = self._current_car()
        owned = car.id in self.profile.get("owned", [])
        selected = self.profile.get("selected") == car.id

        # Header.
        draw_center_text(surface, "GARAGEM AMORIM", get_font(36, bold=True),
                         60, COLOR_ACCENT)

        # Coin balance top-right.
        coin_font = get_font(20, bold=True)
        balance = int(self.profile.get("coins", 0))
        bal_surf = coin_font.render(f"{balance}", True, COLOR_ACCENT)
        bal_rect = bal_surf.get_rect(topright=(WIDTH - 18, 24))
        surface.blit(bal_surf, bal_rect)
        draw_coin_icon(surface, (bal_rect.left - 16, bal_rect.centery), radius=10)

        # Car preview.
        draw_car_preview(surface, (WIDTH // 2, 240), car.body, car.shadow, scale=2.2)

        # Left / right arrows.
        arrow_font = get_font(42, bold=True)
        arrow_color = COLOR_HUD_TEXT
        left = arrow_font.render("<", True, arrow_color)
        right = arrow_font.render(">", True, arrow_color)
        surface.blit(left, left.get_rect(center=(48, 240)))
        surface.blit(right, right.get_rect(center=(WIDTH - 48, 240)))

        # Name + tagline.
        draw_center_text(surface, car.name, get_font(30, bold=True), 360, COLOR_HUD_TEXT)
        draw_center_text(surface, car.tagline, get_font(16, bold=True), 390, COLOR_ACCENT)

        # Stats.
        max_top = max(c.top_speed for c in self.cars)
        max_handling = max(c.handling for c in self.cars)
        stat_rect_speed = pygame.Rect(60, 430, WIDTH - 120, 14)
        stat_rect_hand = pygame.Rect(60, 460, WIDTH - 120, 14)
        draw_stat_bar(surface, stat_rect_speed, "VELOCIDADE", car.top_speed / max_top)
        draw_stat_bar(surface, stat_rect_hand, "AGILIDADE", car.handling / max_handling)

        # Status line (price / owned / selected).
        if selected:
            status = "SELECIONADO"
            status_color = COLOR_ACCENT
        elif owned:
            status = "ENTER para selecionar"
            status_color = COLOR_HUD_TEXT
        else:
            status = f"PRECO  {car.price} MOEDAS  .  ENTER para comprar"
            status_color = COLOR_HUD_TEXT
        draw_center_text(surface, status, get_font(20, bold=True), 520, status_color)

        # Flash message.
        if self.flash_timer > 0 and self.flash_text:
            alpha = self.flash_timer / self.FLASH_DURATION
            font = get_font(28, bold=True)
            text_surf = font.render(self.flash_text, True, self.flash_color)
            text_surf.set_alpha(int(255 * min(1.0, alpha * 2)))
            surface.blit(text_surf, text_surf.get_rect(center=(WIDTH // 2, 570)))

        # Footer hint.
        draw_center_text(surface,
                         "<- ->  navega   .   ENTER escolhe   .   ESC volta",
                         get_font(14, bold=True), HEIGHT - 30, COLOR_HUD_TEXT)

        # Index dots.
        dot_y = 600
        total = len(self.cars)
        start_x = WIDTH // 2 - (total - 1) * 10
        for i in range(total):
            color = COLOR_ACCENT if i == self.index else COLOR_HUD_TEXT
            pygame.draw.circle(surface, color, (start_x + i * 20, dot_y), 5)
