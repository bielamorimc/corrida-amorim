"""Game-wide constants for Corridas Amorim."""
from pathlib import Path

# --- Window ---
WIDTH = 480
HEIGHT = 720
FPS = 60
TITLE = "Corridas Amorim"

# --- Road layout ---
ROAD_LEFT = 60
ROAD_RIGHT = WIDTH - 60
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANE_COUNT = 3
LANE_WIDTH = ROAD_WIDTH / LANE_COUNT
LANES = [int(ROAD_LEFT + LANE_WIDTH * (i + 0.5)) for i in range(LANE_COUNT)]
DASH_LENGTH = 30
DASH_GAP = 24

# --- Entities ---
CAR_WIDTH = 54
CAR_HEIGHT = 96
PLAYER_Y = HEIGHT - 140
LANE_SNAP_SPEED = 14  # px/frame toward target x

# --- Motion / difficulty ---
BASE_SCROLL = 6.0
MAX_DIFFICULTY = 3.0
DIFFICULTY_RAMP_SECONDS = 15.0
SPAWN_BASE_COOLDOWN = 0.95  # seconds
SPAWN_MIN_COOLDOWN = 0.22
ENEMY_SPEED_JITTER = (-1.2, 2.2)
MIN_SPAWN_GAP = 150  # min vertical gap between cars in same lane at spawn

# --- Scoring ---
SCORE_PER_PIXEL = 0.12

# --- Palette ---
COLOR_GRASS = (34, 96, 54)
COLOR_GRASS_DARK = (24, 70, 42)
COLOR_ASPHALT = (43, 43, 43)
COLOR_ASPHALT_DARK = (32, 32, 32)
COLOR_LINE = (242, 209, 78)
COLOR_EDGE = (235, 235, 235)
COLOR_PLAYER = (230, 57, 70)
COLOR_PLAYER_DARK = (160, 30, 44)
COLOR_ENEMY_PALETTE = [
    ((64, 130, 198), (34, 80, 140)),   # blue
    ((242, 180, 40), (170, 120, 20)),  # yellow
    ((90, 180, 100), (48, 110, 60)),   # green
    ((210, 210, 220), (120, 120, 140)),  # silver
    ((150, 60, 180), (90, 30, 110)),   # purple
]
COLOR_HEADLIGHT = (255, 240, 180)
COLOR_TAILLIGHT = (255, 70, 70)
COLOR_WINDOW = (30, 40, 60)
COLOR_HUD_BG = (0, 0, 0, 140)
COLOR_HUD_TEXT = (245, 245, 245)
COLOR_ACCENT = (242, 209, 78)
COLOR_DANGER = (230, 57, 70)
COLOR_MENU_BG_TOP = (12, 14, 30)
COLOR_MENU_BG_BOTTOM = (40, 10, 30)

# --- Coins ---
COIN_RADIUS = 14
COIN_BASE_COOLDOWN = 0.55
COIN_MIN_COOLDOWN = 0.18
COIN_GAP_SAME_LANE = 110
COIN_PICKUP_INFLATE = 4  # player hitbox grows this much vs coins (forgiving)
COLOR_COIN_BRONZE = (205, 127, 50)
COLOR_COIN_BRONZE_DARK = (140, 80, 30)
COLOR_COIN_SILVER = (210, 212, 220)
COLOR_COIN_SILVER_DARK = (140, 142, 150)
COLOR_COIN_GOLD = (255, 215, 70)
COLOR_COIN_GOLD_DARK = (175, 138, 30)
COLOR_COIN_SHINE = (255, 250, 220)
# (value, weight, body, dark)
COIN_TIERS = [
    (1, 70, COLOR_COIN_BRONZE, COLOR_COIN_BRONZE_DARK),
    (5, 25, COLOR_COIN_SILVER, COLOR_COIN_SILVER_DARK),
    (15, 5, COLOR_COIN_GOLD, COLOR_COIN_GOLD_DARK),
]

# --- Paths ---
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
FONTS_DIR = ASSETS / "fonts"
IMAGES_DIR = ASSETS / "images"
SOUNDS_DIR = ASSETS / "sounds"
HIGHSCORE_PATH = ROOT / "highscore.json"  # legacy, migrated on boot
PROFILE_PATH = ROOT / "profile.json"

# --- Story ---
STORY_LINES = [
    "Gabriel Amorim cresceu ouvindo o ronco",
    "dos motores na garagem do pai.",
    "",
    "Hoje ele corre pela Taca Amorim -",
    "a lenda da familia.",
    "",
    "Uma ultima corrida.",
    "Desvie do transito. Nao falhe.",
    "",
    "VAI, GABRIEL!",
]
