"""Car catalog: cosmetic + stat definitions for every selectable car."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Car:
    id: str
    name: str
    price: int
    body: tuple[int, int, int]
    shadow: tuple[int, int, int]
    top_speed: float  # multiplier on scroll speed
    handling: float   # multiplier on lane-snap speed
    tagline: str


CARS: list[Car] = [
    Car(
        id="gabriel",
        name="Amorim Classic",
        price=0,
        body=(230, 57, 70),
        shadow=(160, 30, 44),
        top_speed=1.00,
        handling=1.00,
        tagline="O carro da familia. Equilibrado.",
    ),
    Car(
        id="veloz",
        name="Veloz Turbo",
        price=250,
        body=(242, 180, 40),
        shadow=(170, 120, 20),
        top_speed=1.15,
        handling=1.05,
        tagline="Mais rapido, mais agil. Um foguete.",
    ),
    Car(
        id="phantom",
        name="Phantom GT",
        price=600,
        body=(58, 36, 90),
        shadow=(24, 16, 44),
        top_speed=1.28,
        handling=0.92,
        tagline="Velocidade brutal, curvas traicoeiras.",
    ),
]


_CARS_BY_ID: dict[str, Car] = {c.id: c for c in CARS}


def get_car(car_id: str) -> Car:
    return _CARS_BY_ID.get(car_id, CARS[0])


def car_ids() -> list[str]:
    return [c.id for c in CARS]


def default_car_id() -> str:
    return CARS[0].id


def starting_owned() -> list[str]:
    return [CARS[0].id]
