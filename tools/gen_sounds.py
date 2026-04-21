"""Generate placeholder sound effects using only the stdlib.

Run once: `python tools/gen_sounds.py`. Writes WAVs into assets/sounds/.
Drop-in replace any of these with your own WAVs later.
"""
from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 44100
OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "sounds"


def _write_wav(path: Path, samples: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for s in samples:
            s = max(-1.0, min(1.0, s))
            frames += struct.pack("<h", int(s * 32000))
        wf.writeframes(bytes(frames))


def gen_engine_loop(duration: float = 1.2) -> list[float]:
    n = int(SAMPLE_RATE * duration)
    out: list[float] = []
    for i in range(n):
        t = i / SAMPLE_RATE
        base = math.sin(2 * math.pi * 85 * t)
        harmonic = 0.4 * math.sin(2 * math.pi * 170 * t)
        rumble = 0.3 * math.sin(2 * math.pi * 52 * t + math.sin(t * 3))
        noise = 0.08 * (random.random() * 2 - 1)
        value = (base + harmonic + rumble) * 0.35 + noise
        # Smooth loop edges.
        edge = min(1.0, min(i, n - i - 1) / (SAMPLE_RATE * 0.05))
        out.append(value * edge)
    return out


def gen_crash(duration: float = 0.9) -> list[float]:
    n = int(SAMPLE_RATE * duration)
    out: list[float] = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 4.5)
        noise = (random.random() * 2 - 1)
        thud = math.sin(2 * math.pi * 70 * t) * math.exp(-t * 6)
        out.append((noise * 0.7 + thud * 0.8) * env)
    return out


def gen_click(duration: float = 0.08) -> list[float]:
    n = int(SAMPLE_RATE * duration)
    out: list[float] = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 55)
        value = math.sin(2 * math.pi * 1400 * t) * env
        out.append(value * 0.6)
    return out


def gen_coin(duration: float = 0.22) -> list[float]:
    n = int(SAMPLE_RATE * duration)
    out: list[float] = []
    mid = n // 2
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 988 if i < mid else 1319  # B5 then E6
        env = math.exp(-t * 9)
        value = math.sin(2 * math.pi * freq * t) * env
        out.append(value * 0.55)
    return out


def gen_countdown(duration: float = 0.25) -> list[float]:
    n = int(SAMPLE_RATE * duration)
    out: list[float] = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 8) * (1 if t < 0.18 else 0)
        value = math.sin(2 * math.pi * 880 * t) * env
        out.append(value * 0.5)
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_wav(OUT_DIR / "engine_loop.wav", gen_engine_loop())
    _write_wav(OUT_DIR / "crash.wav", gen_crash())
    _write_wav(OUT_DIR / "click.wav", gen_click())
    _write_wav(OUT_DIR / "countdown.wav", gen_countdown())
    _write_wav(OUT_DIR / "coin.wav", gen_coin())
    print(f"Wrote sounds to {OUT_DIR}")


if __name__ == "__main__":
    main()
