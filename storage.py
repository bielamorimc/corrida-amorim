"""Persistent player profile: high score, coins, owned cars, selection."""
from __future__ import annotations

import json
from typing import Any

from cars import car_ids, default_car_id, starting_owned
from settings import HIGHSCORE_PATH, PROFILE_PATH

DEFAULT_PROFILE: dict[str, Any] = {
    "best": 0,
    "coins": 0,
    "owned": starting_owned(),
    "selected": default_car_id(),
}


def _default_profile() -> dict[str, Any]:
    return {
        "best": 0,
        "coins": 0,
        "owned": starting_owned(),
        "selected": default_car_id(),
    }


def _sanitize(profile: dict[str, Any]) -> dict[str, Any]:
    out = _default_profile()
    try:
        out["best"] = max(0, int(profile.get("best", 0)))
    except (TypeError, ValueError):
        pass
    try:
        out["coins"] = max(0, int(profile.get("coins", 0)))
    except (TypeError, ValueError):
        pass
    valid_ids = set(car_ids())
    owned = profile.get("owned", [])
    if isinstance(owned, list):
        owned_clean = [cid for cid in owned if isinstance(cid, str) and cid in valid_ids]
        if default_car_id() not in owned_clean:
            owned_clean.append(default_car_id())
        out["owned"] = owned_clean
    selected = profile.get("selected")
    if isinstance(selected, str) and selected in out["owned"]:
        out["selected"] = selected
    return out


def load_profile() -> dict[str, Any]:
    # Try current profile file first.
    try:
        with PROFILE_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        profile = _sanitize(data if isinstance(data, dict) else {})
        return profile
    except (FileNotFoundError, ValueError, OSError):
        pass

    # Migrate legacy highscore.json if present.
    legacy_best = 0
    try:
        with HIGHSCORE_PATH.open("r", encoding="utf-8") as f:
            legacy = json.load(f)
        legacy_best = int(legacy.get("best", 0))
    except (FileNotFoundError, ValueError, OSError, TypeError):
        pass

    profile = _default_profile()
    profile["best"] = max(0, legacy_best)
    save_profile(profile)
    return profile


def save_profile(profile: dict[str, Any]) -> None:
    try:
        tmp = PROFILE_PATH.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(_sanitize(profile), f, indent=2)
        tmp.replace(PROFILE_PATH)
    except OSError:
        pass


def add_coins(profile: dict[str, Any], amount: int) -> None:
    profile["coins"] = max(0, int(profile.get("coins", 0)) + int(amount))


def purchase_car(profile: dict[str, Any], car_id: str, price: int) -> bool:
    if car_id in profile.get("owned", []):
        return False
    if profile.get("coins", 0) < price:
        return False
    profile["coins"] = int(profile["coins"]) - int(price)
    profile.setdefault("owned", []).append(car_id)
    profile["selected"] = car_id
    return True


def set_selected(profile: dict[str, Any], car_id: str) -> bool:
    if car_id in profile.get("owned", []):
        profile["selected"] = car_id
        return True
    return False


# --- Backwards-compatible helpers for the older high-score API ---

def load_highscore() -> int:
    return int(load_profile().get("best", 0))


def save_highscore(best: int) -> None:
    profile = load_profile()
    profile["best"] = max(profile.get("best", 0), int(best))
    save_profile(profile)
