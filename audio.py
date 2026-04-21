"""Audio manager with graceful fallbacks when sound files are missing."""
from __future__ import annotations

import pygame

from settings import SOUNDS_DIR


class SoundManager:
    def __init__(self) -> None:
        self.muted = False
        self.engine_channel: pygame.mixer.Channel | None = None
        self.sfx_channel: pygame.mixer.Channel | None = None
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self._engine_playing = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(8)
            self.engine_channel = pygame.mixer.Channel(0)
            self.sfx_channel = pygame.mixer.Channel(1)
        except pygame.error:
            # Audio device unavailable; run silently.
            self.engine_channel = None
            self.sfx_channel = None

        for name in ("engine_loop", "crash", "click", "countdown", "coin"):
            path = SOUNDS_DIR / f"{name}.wav"
            if path.exists():
                try:
                    self.sounds[name] = pygame.mixer.Sound(str(path))
                except pygame.error:
                    pass

    def toggle_mute(self) -> None:
        self.muted = not self.muted
        if self.muted:
            if self.engine_channel:
                self.engine_channel.set_volume(0)
            if self.sfx_channel:
                self.sfx_channel.set_volume(0)
        else:
            if self.engine_channel:
                self.engine_channel.set_volume(0.35)
            if self.sfx_channel:
                self.sfx_channel.set_volume(0.75)

    def start_engine(self) -> None:
        if self._engine_playing or self.engine_channel is None:
            return
        snd = self.sounds.get("engine_loop")
        if snd is None:
            return
        self.engine_channel.play(snd, loops=-1)
        self.engine_channel.set_volume(0 if self.muted else 0.35)
        self._engine_playing = True

    def stop_engine(self) -> None:
        if self.engine_channel is not None:
            self.engine_channel.stop()
        self._engine_playing = False

    def set_engine_intensity(self, intensity: float) -> None:
        """intensity in [0,1]; scales engine volume subtly."""
        if self.muted or self.engine_channel is None or not self._engine_playing:
            return
        vol = 0.25 + 0.25 * max(0.0, min(1.0, intensity))
        self.engine_channel.set_volume(vol)

    def play(self, name: str) -> None:
        if self.muted or self.sfx_channel is None:
            return
        snd = self.sounds.get(name)
        if snd is not None:
            self.sfx_channel.play(snd)
