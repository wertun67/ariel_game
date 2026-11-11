import array
import math
import os
import random
import sys

import pygame

# Инициализация
try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.init()
    AUDIO_OK = True
except:
    pygame.init()
    AUDIO_OK = False

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ариэль: Миры за экраном")
clock = pygame.time.Clock()

# --- МУЗЫКА ---
current_music = None


def play_music(track_name):
    global current_music
    if current_music == track_name:
        return
    try:
        if os.path.exists(f"{track_name}.mp3"):
            pygame.mixer.music.load(f"{track_name}.mp3")
        elif os.path.exists(f"{track_name}.ogg"):
            pygame.mixer.music.load(f"{track_name}.ogg")
        else:
            return
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
        current_music = track_name
    except:
        pass


def play_menu_music():
    play_music("menu_music")


def play_boss_music():
    if os.path.exists("boss_music.mp3") or os.path.exists("boss_music.ogg"):
        play_music("boss_music")
    else:
        play_menu_music()


# --- ЗВУКИ ---
def generate_sound(freq, duration, volume=0.2, wave="triangle"):
    if not AUDIO_OK:
        return None
    try:
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = array.array("h")
        for i in range(n_samples):
            t = i / sample_rate
            if wave == "triangle":
                val = 2 * abs(2 * (t * freq - math.floor(t * freq + 0.5))) - 1
                val = int(val * 32767)
            elif wave == "sine":
                val = int(math.sin(freq * 2 * math.pi * t) * 32767)
            elif wave == "noise":
                val = random.randint(-32767, 32767)
            elif wave == "square":
                val = 32767 if math.sin(freq * 2 * math.pi * t) > 0 else -32767
            fade = 1.0 - (i / n_samples)
            val = int(val * volume * fade)
            buf.append(val)
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf.tobytes())
    except:
        return None


snd_hit = generate_sound(600, 0.08, 0.2, "triangle")
snd_hurt = generate_sound(200, 0.15, 0.3, "sine")
snd_heal = generate_sound(500, 0.2, 0.2, "sine")
snd_crit = generate_sound(900, 0.1, 0.25, "triangle")
snd_death = generate_sound(150, 0.3, 0.3, "triangle")
snd_win = generate_sound(800, 0.4, 0.25, "sine")
snd_poison = generate_sound(250, 0.15, 0.2, "sine")

sound_cooldown = 0

# Цвета
BLACK = (15, 15, 20)
RED = (200, 30, 40)
WHITE = (240, 240, 240)
WALL = (40, 40, 50)
WALL_HIGHLIGHT = (60, 60, 70)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (150, 50, 200)
BLUE = (50, 100, 255)
ORANGE = (255, 165, 0)
DOOR_COLOR = (100, 50, 150)
BOSS_DOOR_COLOR = (200, 100, 50)
BATTLE_BG = (25, 25, 35)
BOX_BORDER = (150, 150, 150)
FLASH_COLOR = (255, 255, 255)
DEATH_BG = (50, 10, 10)
WIN_BG = (10, 40, 20)
SKIN = (220, 200, 180)
HAIR = (180, 20, 20)
SUIT = (30, 30, 40)
KNIFE = (200, 200, 210)
ARMOR_COLOR = (200, 150, 50)
POISON_COLOR = (100, 200, 50)
ROBOT_BODY = (45, 45, 120)
BTN_COLOR = (60, 60, 80)
BTN_ACTIVE = (100, 100, 120)

font = pygame.font.SysFont("Arial", 30, bold=True)
small_font = pygame.font.SysFont("Arial", 20)
title_font = pygame.font.SysFont("Arial", 70, bold=True)

# Состояния
STATE_PLATFORM_SELECT = "platform_select"
STATE_MENU = "menu"
STATE_OVERWORLD = "overworld"
STATE_DIALOGUE = "dialogue"
STATE_BATTLE = "battle"
STATE_ATTACK = "attack"
STATE_TIMING = "timing"
STATE_WIN = "win"
STATE_DEAD = "dead"
STATE_END_KILL = "end_kill"
STATE_END_MERCY = "end_mercy"
current_state = STATE_PLATFORM_SELECT
is_mobile = False

# Игрок
player_size = 40
player_x, player_y = 400, 300
player_speed = 5
player_hp, player_max_hp = 50, 50
has_armor = False
poison_timer = 0

# Бой
battle_selected = -1
battle_options = ["FIGHT (F)", "ACT (A)", "ITEM (I)", "MERCY (M)"]
active_enemy = None
battle_message = ""
box_rect = pygame.Rect(200, 350, 400, 150)
ariel_battle_rect = pygame.Rect(0, 0, 20, 20)
ariel_battle_rect.center = box_rect.center
battle_speed = 6
projectiles = []
projectile_timer = 0
attack_duration = 180
mercy_counter = 0

# Анимация
attack_anim_timer = 0
enemy_hit_flash = 0

# Тайминг
timing_cursor = 0
timing_direction = 1
timing_speed = 7

# Диалоги
current_dialogue = ""
dialogue_timer = 0
next_state_after_dialogue = ""
boss_to_fight = None

# Эффекты
shake_timer = 0
ariel_flash_timer = 0
enemy_pulse = 0
particles = []
enemy_breath = 0

# Мобильные кнопки
btn_up = pygame.Rect(70, 480, 50, 50)
btn_down = pygame.Rect(70, 560, 50, 50)
btn_left = pygame.Rect(10, 520, 50, 50)
btn_right = pygame.Rect(130, 520, 50, 50)

btn_fight = pygame.Rect(20, 520, 180, 60)
btn_act = pygame.Rect(210, 520, 180, 60)
btn_item = pygame.Rect(400, 520, 180, 60)
btn_mercy = pygame.Rect(590, 520, 180, 60)


# Комнаты
def get_initial_rooms():
    return {
        0: {
            "walls": [
                [0, 0, 800, 20],
                [0, 0, 20, 600],
                [780, 0, 20, 600],
                [0, 580, 800, 20],
            ],
            "enemies": [
                {"x": 400, "y": 200, "hp": 50, "name": "Бот Ярик", "type": "shooter"}
            ],
            "doors": [
                {
                    "rect": [750, 250, 30, 100],
                    "target_room": 1,
                    "spawn_x": 50,
                    "spawn_y": 300,
                    "color": DOOR_COLOR,
                }
            ],
        },
        1: {
            "walls": [
                [0, 0, 800, 20],
                [0, 0, 20, 600],
                [780, 0, 20, 600],
                [0, 580, 800, 20],
                [100, 100, 20, 400],
                [100, 100, 300, 20],
                [400, 100, 20, 200],
                [600, 100, 20, 400],
                [200, 500, 400, 20],
                [200, 200, 100, 20],
                [500, 300, 100, 20],
                [300, 400, 20, 100],
                [700, 300, 60, 20],
            ],
            "enemies": [],
            "doors": [
                {
                    "rect": [20, 250, 30, 100],
                    "target_room": 0,
                    "spawn_x": 700,
                    "spawn_y": 300,
                    "color": DOOR_COLOR,
                },
                {
                    "rect": [750, 500, 30, 100],
                    "target_room": 2,
                    "spawn_x": 50,
                    "spawn_y": 300,
                    "color": DOOR_COLOR,
                },
            ],
        },
        2: {
            "walls": [
                [0, 0, 800, 20],
                [0, 0, 20, 600],
                [780, 0, 20, 600],
                [0, 580, 800, 20],
                [200, 0, 20, 400],
                [200, 500, 400, 20],
                [400, 200, 20, 300],
                [600, 100, 20, 400],
                [700, 200, 80, 20],
            ],
            "enemies": [
                {"x": 600, "y": 300, "hp": 40, "name": "Тень", "type": "laser"}
            ],
            "doors": [
                {
                    "rect": [20, 250, 30, 100],
                    "target_room": 1,
                    "spawn_x": 700,
                    "spawn_y": 500,
                    "color": DOOR_COLOR,
                },
                {
                    "rect": [750, 500, 30, 100],
                    "target_room": 3,
                    "spawn_x": 50,
                    "spawn_y": 300,
                    "color": DOOR_COLOR,
                },
            ],
        },
        3: {
            "walls": [
                [0, 0, 800, 20],
                [0, 0, 20, 600],
                [780, 0, 20, 600],
                [0, 580, 800, 20],
                [350, 0, 100, 300],
            ],
            "enemies": [
                {"x": 400, "y": 300, "hp": 45, "name": "Вирус", "type": "poison"}
            ],
            "doors": [
                {
                    "rect": [20, 250, 30, 100],
                    "target_room": 2,
                    "spawn_x": 700,
                    "spawn_y": 500,
                    "color": DOOR_COLOR,
                },
                {
                    "rect": [750, 250, 30, 100],
                    "target_room": 4,
                    "spawn_x": 50,
                    "spawn_y": 300,
                    "color": BOSS_DOOR_COLOR,
                },
            ],
        },
        4: {
            "walls": [
                [0, 0, 800, 20],
                [0, 0, 20, 600],
                [780, 0, 20, 600],
                [0, 580, 800, 20],
                [300, 500, 200, 20],
            ],
            "enemies": [
                {
                    "x": 400,
                    "y": 300,
                    "hp": 80,
                    "name": "Демон-Кот Лёшенка",
                    "type": "dual",
                    "drops_armor": True,
                }
            ],
            "doors": [
                {
                    "rect": [20, 250, 30, 100],
                    "target_room": 3,
                    "spawn_x": 700,
                    "spawn_y": 300,
                    "color": DOOR_COLOR,
                },
                {
                    "rect": [750, 250, 30, 100],
                    "target_room": 5,
                    "spawn_x": 50,
                    "spawn_y": 300,
                    "color": BOSS_DOOR_COLOR,
                },
            ],
        },
        5: {
            "walls": [
                [0, 0, 800, 20],
                [0, 0, 20, 600],
                [780, 0, 20, 600],
                [0, 580, 800, 20],
                [100, 100, 200, 50],
                [500, 450, 200, 50],
            ],
            "enemies": [
                {"x": 400, "y": 300, "hp": 120, "name": "Робот Стёпа", "type": "boss"}
            ],
            "doors": [
                {
                    "rect": [20, 250, 30, 100],
                    "target_room": 4,
                    "spawn_x": 700,
                    "spawn_y": 300,
                    "color": DOOR_COLOR,
                }
            ],
        },
    }


rooms = get_initial_rooms()
current_room = 0


def reset_game():
    global \
        rooms, \
        current_room, \
        player_x, \
        player_y, \
        player_hp, \
        current_state, \
        active_enemy
    global \
        projectile_timer, \
        shake_timer, \
        particles, \
        projectiles, \
        has_armor, \
        poison_timer, \
        sound_cooldown, \
        mercy_counter
    global \
        current_dialogue, \
        dialogue_timer, \
        next_state_after_dialogue, \
        boss_to_fight, \
        current_music
    rooms = get_initial_rooms()
    current_room = 0
    player_x, player_y = 400, 300
    player_hp = player_max_hp
    has_armor = False
    poison_timer = 0
    sound_cooldown = 0
    mercy_counter = 0
    current_state = STATE_OVERWORLD
    active_enemy = None
    projectile_timer = 0
    shake_timer = 0
    particles.clear()
    projectiles.clear()
    ariel_battle_rect.center = box_rect.center
    current_music = None
    play_menu_music()


def draw_ariel(surface, rect, is_battle=False, attacking=False):
    x, y, w, h = rect
    pygame.draw.ellipse(surface, (5, 5, 5), (x + 5, y + h - 5, 30, 10))
    pygame.draw.polygon(
        surface,
        (20, 20, 30),
        [(x + 5, y + 15), (x + 35, y + 15), (x + 35, y + 40), (x + 5, y + 40)],
    )
    pygame.draw.polygon(
        surface,
        (40, 40, 50),
        [(x + 10, y + 15), (x + 30, y + 15), (x + 30, y + 40), (x + 10, y + 40)],
    )
    pygame.draw.rect(surface, (200, 20, 20), (x + 8, y + 12, 24, 6))
    pygame.draw.polygon(
        surface, (200, 20, 20), [(x + 30, y + 12), (x + 38, y + 18), (x + 30, y + 22)]
    )
    pygame.draw.rect(surface, SKIN, (x + 10, y + 4, 20, 12))
    pygame.draw.polygon(
        surface,
        HAIR,
        [
            (x + 5, y),
            (x + 35, y),
            (x + 35, y + 8),
            (x + 30, y + 6),
            (x + 25, y + 10),
            (x + 15, y + 6),
            (x + 5, y + 8),
        ],
    )
    pygame.draw.polygon(
        surface, HAIR, [(x + 5, y + 5), (x + 10, y + 15), (x + 5, y + 15)]
    )
    pygame.draw.polygon(
        surface, HAIR, [(x + 35, y + 5), (x + 30, y + 15), (x + 35, y + 15)]
    )
    pygame.draw.polygon(
        surface, BLACK, [(x + 14, y + 8), (x + 18, y + 9), (x + 14, y + 10)]
    )
    pygame.draw.polygon(
        surface, BLACK, [(x + 26, y + 8), (x + 22, y + 9), (x + 26, y + 10)]
    )
    if has_armor and is_battle:
        pygame.draw.rect(surface, ARMOR_COLOR, (x + 4, y + 14, 32, 27), 2)
    if attacking and not is_battle:
        pygame.draw.polygon(
            surface, KNIFE, [(x + 40, y + 15), (x + 60, y + 10), (x + 45, y + 22)]
        )
        pygame.draw.rect(surface, (100, 50, 20), (x + 35, y + 18, 8, 5))
    elif not is_battle:
        pygame.draw.polygon(
            surface, KNIFE, [(x + 35, y + 20), (x + 50, y + 15), (x + 40, y + 25)]
        )
        pygame.draw.rect(surface, (100, 50, 20), (x + 32, y + 22, 5, 5))


def draw_enemy(surface, rect, enemy_type, pulse, flash):
    x, y, w, h = rect
    cx, cy = x + w // 2, y + h // 2
    if enemy_type == "shooter":
        pygame.draw.rect(surface, (30, 30, 45), (x, y, w, h), border_radius=10)
        pygame.draw.rect(
            surface,
            (60, 60, 80),
            (x + w * 0.1, y + h * 0.1, w * 0.8, h * 0.8),
            border_radius=5,
        )
        eye_color = RED if flash else YELLOW
        pygame.draw.polygon(
            surface,
            eye_color,
            [
                (x + w * 0.2, y + h * 0.3),
                (x + w * 0.4, y + h * 0.4),
                (x + w * 0.2, y + h * 0.5),
            ],
        )
        pygame.draw.polygon(
            surface,
            eye_color,
            [
                (x + w * 0.8, y + h * 0.3),
                (x + w * 0.6, y + h * 0.4),
                (x + w * 0.8, y + h * 0.5),
            ],
        )
        pygame.draw.line(surface, (150, 150, 150), (cx, y), (cx, y - h * 0.2), 4)
        pygame.draw.circle(surface, RED, (cx, y - h * 0.2), w * 0.06)
    elif enemy_type == "laser":
        pygame.draw.circle(surface, (15, 15, 20), (cx, cy), w * 0.5)
        pygame.draw.polygon(
            surface,
            (10, 10, 15),
            [(x, y + h), (x + w, y + h), (x + w, y + h * 0.4), (x, y + h * 0.4)],
        )
        pygame.draw.ellipse(
            surface, YELLOW, (cx - w * 0.25, cy - h * 0.05, w * 0.15, h * 0.08)
        )
        pygame.draw.ellipse(
            surface, YELLOW, (cx + w * 0.1, cy - h * 0.05, w * 0.15, h * 0.08)
        )
    elif enemy_type == "dual":
        pygame.draw.ellipse(
            surface, (240, 240, 245), (cx - w * 0.4, cy, w * 0.8, h * 0.5)
        )
        pygame.draw.circle(surface, (240, 240, 245), (cx, cy - h * 0.1), w * 0.35)
        pygame.draw.polygon(
            surface,
            (240, 240, 245),
            [
                (cx - w * 0.35, cy - h * 0.2),
                (cx - w * 0.15, cy - h * 0.2),
                (cx - w * 0.25, cy - h * 0.55),
            ],
        )
        pygame.draw.polygon(
            surface,
            (240, 240, 245),
            [
                (cx + w * 0.35, cy - h * 0.2),
                (cx + w * 0.15, cy - h * 0.2),
                (cx + w * 0.25, cy - h * 0.55),
            ],
        )
        pygame.draw.polygon(
            surface,
            (200, 100, 150),
            [
                (cx - w * 0.3, cy - h * 0.25),
                (cx - w * 0.2, cy - h * 0.25),
                (cx - w * 0.25, cy - h * 0.45),
            ],
        )
        pygame.draw.polygon(
            surface,
            (200, 100, 150),
            [
                (cx + w * 0.3, cy - h * 0.25),
                (cx + w * 0.2, cy - h * 0.25),
                (cx + w * 0.25, cy - h * 0.45),
            ],
        )
        pygame.draw.polygon(
            surface,
            RED,
            [
                (cx - w * 0.2, cy - h * 0.15),
                (cx - w * 0.1, cy - h * 0.1),
                (cx - w * 0.2, cy - h * 0.05),
            ],
        )
        pygame.draw.polygon(
            surface,
            RED,
            [
                (cx + w * 0.2, cy - h * 0.15),
                (cx + w * 0.1, cy - h * 0.1),
                (cx + w * 0.2, cy - h * 0.05),
            ],
        )
        pygame.draw.polygon(
            surface,
            (255, 150, 150),
            [(cx, cy), (cx - w * 0.05, cy + h * 0.05), (cx + w * 0.05, cy + h * 0.05)],
        )
        pygame.draw.line(
            surface,
            BLACK,
            (cx - w * 0.1, cy + h * 0.1),
            (cx - w * 0.3, cy + h * 0.05),
            1,
        )
        pygame.draw.line(
            surface,
            BLACK,
            (cx + w * 0.1, cy + h * 0.1),
            (cx + w * 0.3, cy + h * 0.05),
            1,
        )
    elif enemy_type == "poison":
        pygame.draw.circle(surface, (40, 180, 40), (cx, cy), w * 0.45)
        pygame.draw.circle(surface, (100, 255, 100), (cx, cy), w * 0.35)
        pygame.draw.ellipse(
            surface, WHITE, (cx - w * 0.2, cy - h * 0.2, w * 0.4, h * 0.2)
        )
        pygame.draw.circle(surface, RED, (cx, cy - h * 0.1), w * 0.08)
        pygame.draw.circle(surface, BLACK, (cx, cy - h * 0.1), w * 0.04)
        pygame.draw.line(
            surface,
            (40, 180, 40),
            (cx - w * 0.3, cy - h * 0.3),
            (cx - w * 0.5, cy - h * 0.5),
            5,
        )
        pygame.draw.line(
            surface,
            (40, 180, 40),
            (cx + w * 0.3, cy - h * 0.3),
            (cx + w * 0.5, cy - h * 0.5),
            5,
        )
        pygame.draw.line(
            surface,
            (40, 180, 40),
            (cx - w * 0.3, cy + h * 0.3),
            (cx - w * 0.4, cy + h * 0.5),
            5,
        )
    elif enemy_type == "boss":
        pygame.draw.rect(
            surface,
            (80, 80, 100),
            (x - w * 0.05, cy, w * 0.15, h * 0.3),
            border_radius=5,
        )
        pygame.draw.rect(
            surface,
            (80, 80, 100),
            (x + w * 0.9, cy, w * 0.15, h * 0.3),
            border_radius=5,
        )
        pygame.draw.circle(
            surface, (120, 120, 140), (x - w * 0.05, cy + h * 0.3), w * 0.08
        )
        pygame.draw.circle(
            surface, (120, 120, 140), (x + w * 1.05, cy + h * 0.3), w * 0.08
        )
        pygame.draw.rect(
            surface,
            (45, 45, 120),
            (x + w * 0.1, cy - h * 0.05, w * 0.8, h * 0.45),
            border_radius=15,
        )
        pygame.draw.rect(
            surface,
            (20, 20, 60),
            (x + w * 0.1, cy - h * 0.05, w * 0.8, h * 0.45),
            4,
            border_radius=15,
        )
        pygame.draw.rect(
            surface,
            (100, 200, 255),
            (cx - w * 0.15, cy + h * 0.1, w * 0.3, h * 0.1),
            border_radius=3,
        )
        pygame.draw.circle(surface, (30, 30, 50), (cx, cy - h * 0.15), w * 0.3)
        pygame.draw.circle(surface, (100, 150, 255), (cx, cy - h * 0.15), w * 0.3, 3)
        pygame.draw.ellipse(
            surface, (220, 220, 230), (cx - w * 0.15, cy - h * 0.1, w * 0.3, h * 0.15)
        )
        pygame.draw.circle(surface, (220, 220, 230), (cx, cy - h * 0.15), w * 0.12)
        pygame.draw.polygon(
            surface,
            (220, 220, 230),
            [
                (cx - w * 0.12, cy - h * 0.2),
                (cx - w * 0.05, cy - h * 0.2),
                (cx - w * 0.08, cy - h * 0.28),
            ],
        )
        pygame.draw.polygon(
            surface,
            (220, 220, 230),
            [
                (cx + w * 0.12, cy - h * 0.2),
                (cx + w * 0.05, cy - h * 0.2),
                (cx + w * 0.08, cy - h * 0.28),
            ],
        )
        pygame.draw.circle(surface, BLACK, (cx - w * 0.04, cy - h * 0.15), w * 0.02)
        pygame.draw.circle(surface, BLACK, (cx + w * 0.04, cy - h * 0.15), w * 0.02)
        pygame.draw.line(
            surface,
            (150, 150, 150),
            (cx - w * 0.2, cy - h * 0.4),
            (cx - w * 0.25, cy - h * 0.55),
            3,
        )
        pygame.draw.line(
            surface,
            (150, 150, 150),
            (cx + w * 0.2, cy - h * 0.4),
            (cx + w * 0.25, cy - h * 0.55),
            3,
        )
        pygame.draw.circle(
            surface, RED if flash else YELLOW, (cx - w * 0.25, cy - h * 0.55), w * 0.04
        )
        pygame.draw.circle(
            surface, RED if flash else YELLOW, (cx + w * 0.25, cy - h * 0.55), w * 0.04
        )


def check_collision(new_x, new_y):
    if new_x < 0 or new_x + player_size > 800 or new_y < 0 or new_y + player_size > 600:
        return True
    for wall in rooms[current_room]["walls"]:
        if (
            new_x < wall[0] + wall[2]
            and new_x + player_size > wall[0]
            and new_y < wall[1] + wall[3]
            and new_y + player_size > wall[1]
        ):
            return True
    return False


def reset_battle():
    global \
        projectiles, \
        projectile_timer, \
        shake_timer, \
        particles, \
        attack_anim_timer, \
        enemy_hit_flash, \
        poison_timer, \
        sound_cooldown
    projectiles.clear()
    particles.clear()
    projectile_timer = 0
    shake_timer = 0
    attack_anim_timer = 0
    enemy_hit_flash = 0
    poison_timer = 0
    sound_cooldown = 0
    ariel_battle_rect.center = box_rect.center


def spawn_particles(x, y, color, count=20):
    for _ in range(count):
        particles.append(
            {
                "x": x,
                "y": y,
                "vx": random.uniform(-6, 6),
                "vy": random.uniform(-6, 6),
                "timer": 30,
                "color": color,
            }
        )


def draw_mobile_buttons(surface, state):
    if state == STATE_OVERWORLD:
        pygame.draw.rect(surface, BTN_COLOR, btn_up, border_radius=10)
        pygame.draw.rect(surface, BTN_COLOR, btn_down, border_radius=10)
        pygame.draw.rect(surface, BTN_COLOR, btn_left, border_radius=10)
        pygame.draw.rect(surface, BTN_COLOR, btn_right, border_radius=10)
        pygame.draw.polygon(
            surface,
            WHITE,
            [
                (btn_up.centerx, btn_up.top + 10),
                (btn_up.left + 10, btn_up.bottom - 10),
                (btn_up.right - 10, btn_up.bottom - 10),
            ],
        )
        pygame.draw.polygon(
            surface,
            WHITE,
            [
                (btn_down.centerx, btn_down.bottom - 10),
                (btn_down.left + 10, btn_down.top + 10),
                (btn_down.right - 10, btn_down.top + 10),
            ],
        )
        pygame.draw.polygon(
            surface,
            WHITE,
            [
                (btn_left.left + 10, btn_left.centery),
                (btn_left.right - 10, btn_left.top + 10),
                (btn_left.right - 10, btn_left.bottom - 10),
            ],
        )
        pygame.draw.polygon(
            surface,
            WHITE,
            [
                (btn_right.right - 10, btn_right.centery),
                (btn_right.left + 10, btn_right.top + 10),
                (btn_right.left + 10, btn_right.bottom - 10),
            ],
        )
    elif state == STATE_BATTLE:
        for rect, text in [
            (btn_fight, "FIGHT"),
            (btn_act, "ACT"),
            (btn_item, "ITEM"),
            (btn_mercy, "MERCY"),
        ]:
            pygame.draw.rect(
                surface,
                BTN_ACTIVE
                if text == battle_options[battle_selected].split()[0]
                else BTN_COLOR,
                rect,
                border_radius=10,
            )
            pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)
            txt = font.render(text, True, WHITE)
            surface.blit(txt, txt.get_rect(center=rect.center))
    elif state == STATE_DIALOGUE or state == STATE_TIMING:
        pygame.draw.rect(surface, BTN_COLOR, (0, 550, 800, 50))
        pygame.draw.rect(surface, WHITE, (0, 550, 800, 50), 2)
        txt = font.render("НАЖМИ СЮДА", True, YELLOW)
        surface.blit(txt, txt.get_rect(center=(400, 575)))


# --- ГЛАВНЫЙ ЦИКЛ ---
running = True
while running:
    shake_x, shake_y = 0, 0
    if shake_timer > 0:
        shake_x = random.randint(-10, 10)
        shake_y = random.randint(-10, 10)
        shake_timer -= 1

    if sound_cooldown > 0:
        sound_cooldown -= 1

    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_click = True
        elif event.type == pygame.KEYDOWN:
            if current_state == STATE_MENU:
                if event.key == pygame.K_RETURN:
                    reset_game()
            elif current_state == STATE_DIALOGUE:
                if event.key == pygame.K_RETURN:
                    current_state = next_state_after_dialogue
                    if current_state == STATE_BATTLE:
                        active_enemy = boss_to_fight
                        battle_message = f"Навстречу выходит {active_enemy['name']}!"
                        battle_selected = -1
                        reset_battle()
            elif (
                current_state == STATE_BATTLE
                and active_enemy
                and active_enemy["hp"] > 0
            ):
                if event.key == pygame.K_f:
                    battle_message = "ЖМИ ENTER!"
                    current_state = STATE_TIMING
                    timing_cursor = 0
                    timing_direction = 1
                elif event.key == pygame.K_a:
                    battle_message = "Ариэль договаривается..."
                    battle_selected = 1
                    current_state = STATE_ATTACK
                    reset_battle()
                elif event.key == pygame.K_i:
                    player_hp = min(player_max_hp, player_hp + 15)
                    battle_message = "Тоник! (+15 HP)"
                    battle_selected = 2
                    current_state = STATE_ATTACK
                    reset_battle()
                    if snd_heal and sound_cooldown == 0:
                        snd_heal.play()
                        sound_cooldown = 15
                elif event.key == pygame.K_m:
                    if active_enemy["name"] == "Робот Стёпа":
                        mercy_counter += 1
                        if mercy_counter >= 3:
                            current_state = STATE_END_MERCY
                            battle_message = "Стёпа отключает питание..."
                        else:
                            battle_message = f"Пощада... ({mercy_counter}/3)"
                            current_state = STATE_ATTACK
                            reset_battle()
                    else:
                        battle_message = "Пощады не будет..."
                        battle_selected = 3
                        current_state = STATE_ATTACK
                        reset_battle()
            elif current_state == STATE_TIMING:
                if event.key == pygame.K_RETURN:
                    if 180 <= timing_cursor <= 220:
                        damage = random.randint(25, 35)
                        snd_crit.play() if snd_crit else None
                        enemy_pulse = 25
                        attack_anim_timer = 15
                        enemy_hit_flash = 10
                    elif 120 <= timing_cursor <= 280:
                        damage = random.randint(10, 20)
                        snd_hit.play() if snd_hit else None
                        enemy_pulse = 15
                        attack_anim_timer = 15
                        enemy_hit_flash = 10
                    else:
                        damage = 0
                        snd_hit.play() if snd_hit else None
                    active_enemy["hp"] -= damage
                    battle_message = f"Удар! (-{damage} HP)"
                    current_state = STATE_ATTACK
                    reset_battle()
            elif current_state == STATE_WIN:
                if event.key == pygame.K_RETURN:
                    if active_enemy and active_enemy["name"] == "Робот Стёпа":
                        current_state = STATE_END_KILL
                        play_menu_music()
                    else:
                        current_state = STATE_OVERWORLD
                        player_y += 60
                        active_enemy = None
                        reset_battle()
                        play_menu_music()
            elif current_state in [STATE_DEAD, STATE_END_KILL, STATE_END_MERCY]:
                if event.key == pygame.K_RETURN:
                    reset_game()

    # Мобильное управление
    if mouse_click:
        if current_state == STATE_PLATFORM_SELECT:
            if pygame.Rect(150, 250, 200, 80).collidepoint(mouse_pos):
                is_mobile = False
                current_state = STATE_MENU
                play_menu_music()
            elif pygame.Rect(450, 250, 200, 80).collidepoint(mouse_pos):
                is_mobile = True
                current_state = STATE_MENU
                play_menu_music()
        elif current_state == STATE_MENU:
            reset_game()
        elif current_state == STATE_OVERWORLD:
            if btn_up.collidepoint(mouse_pos):
                player_y -= player_speed
            elif btn_down.collidepoint(mouse_pos):
                player_y += player_speed
            elif btn_left.collidepoint(mouse_pos):
                player_x -= player_speed
            elif btn_right.collidepoint(mouse_pos):
                player_x += player_speed
            if not check_collision(player_x, player_y):
                pass
        elif current_state == STATE_BATTLE and active_enemy and active_enemy["hp"] > 0:
            if btn_fight.collidepoint(mouse_pos):
                battle_message = "ЖМИ НА ЭКРАН!"
                current_state = STATE_TIMING
                timing_cursor = 0
                timing_direction = 1
                battle_selected = 0
            elif btn_act.collidepoint(mouse_pos):
                battle_message = "Ариэль договаривается..."
                battle_selected = 1
                current_state = STATE_ATTACK
                reset_battle()
            elif btn_item.collidepoint(mouse_pos):
                player_hp = min(player_max_hp, player_hp + 15)
                battle_message = "Тоник! (+15 HP)"
                battle_selected = 2
                current_state = STATE_ATTACK
                reset_battle()
                if snd_heal and sound_cooldown == 0:
                    snd_heal.play()
                    sound_cooldown = 15
            elif btn_mercy.collidepoint(mouse_pos):
                if active_enemy["name"] == "Робот Стёпа":
                    mercy_counter += 1
                    if mercy_counter >= 3:
                        current_state = STATE_END_MERCY
                        battle_message = "Стёпа отключает питание..."
                    else:
                        battle_message = f"Пощада... ({mercy_counter}/3)"
                        current_state = STATE_ATTACK
                        reset_battle()
                else:
                    battle_message = "Пощады не будет..."
                    battle_selected = 3
                    current_state = STATE_ATTACK
                    reset_battle()
        elif current_state in [
            STATE_DIALOGUE,
            STATE_TIMING,
            STATE_WIN,
            STATE_DEAD,
            STATE_END_KILL,
            STATE_END_MERCY,
        ]:
            if mouse_pos[1] > 500:
                if current_state == STATE_DIALOGUE:
                    current_state = next_state_after_dialogue
                    if current_state == STATE_BATTLE:
                        active_enemy = boss_to_fight
                        battle_message = f"Навстречу выходит {active_enemy['name']}!"
                        battle_selected = -1
                        reset_battle()
                elif current_state == STATE_TIMING:
                    if 180 <= timing_cursor <= 220:
                        damage = random.randint(25, 35)
                        snd_crit.play() if snd_crit else None
                        enemy_pulse = 25
                        attack_anim_timer = 15
                        enemy_hit_flash = 10
                    elif 120 <= timing_cursor <= 280:
                        damage = random.randint(10, 20)
                        snd_hit.play() if snd_hit else None
                        enemy_pulse = 15
                        attack_anim_timer = 15
                        enemy_hit_flash = 10
                    else:
                        damage = 0
                        snd_hit.play() if snd_hit else None
                    active_enemy["hp"] -= damage
                    battle_message = f"Удар! (-{damage} HP)"
                    current_state = STATE_ATTACK
                    reset_battle()
                elif current_state == STATE_WIN:
                    if active_enemy and active_enemy["name"] == "Робот Стёпа":
                        current_state = STATE_END_KILL
                        play_menu_music()
                    else:
                        current_state = STATE_OVERWORLD
                        player_y += 60
                        active_enemy = None
                        reset_battle()
                        play_menu_music()
                elif current_state in [STATE_DEAD, STATE_END_KILL, STATE_END_MERCY]:
                    reset_game()

    if current_state == STATE_OVERWORLD and not is_mobile:
        keys = pygame.key.get_pressed()
        new_x, new_y = player_x, player_y
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_x += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            new_y -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_y += player_speed
        if not check_collision(new_x, player_y):
            player_x = new_x
        if not check_collision(player_x, new_y):
            player_y = new_y

    if current_state == STATE_OVERWORLD:
        p_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        for enemy in rooms[current_room]["enemies"]:
            if enemy["hp"] > 0:
                e_rect = pygame.Rect(enemy["x"], enemy["y"], 40, 40)
                if p_rect.colliderect(e_rect):
                    if enemy["name"] in ["Демон-Кот Лёшенка", "Робот Стёпа"]:
                        play_boss_music()
                        current_state = STATE_DIALOGUE
                        current_dialogue = (
                            "Лёшенка: Мяу... Ты пришел за бронёй? Забери её, если сможешь."
                            if enemy["name"] == "Демон-Кот Лёшенка"
                            else "Робот Стёпа: Ариэль... Твои чувства — это баг в системе. Переходи на темную сторону."
                        )
                        next_state_after_dialogue = STATE_BATTLE
                        boss_to_fight = enemy
                    else:
                        current_state = STATE_BATTLE
                        active_enemy = enemy
                        battle_message = f"Навстречу выходит {enemy['name']}!"
                        battle_selected = -1
                        reset_battle()
                    break
        for door in rooms[current_room]["doors"]:
            d_rect = pygame.Rect(door["rect"])
            if p_rect.colliderect(d_rect):
                current_room = door["target_room"]
                player_x = door["spawn_x"]
                player_y = door["spawn_y"]
                reset_battle()
                break

    elif current_state == STATE_DIALOGUE:
        dialogue_timer += 1
    elif current_state == STATE_TIMING:
        timing_cursor += timing_direction * timing_speed
        if timing_cursor >= 390:
            timing_cursor = 390
            timing_direction = -1
        elif timing_cursor <= 0:
            timing_cursor = 0
            timing_direction = 1

    elif current_state == STATE_ATTACK:
        if attack_anim_timer > 0:
            attack_anim_timer -= 1
        if enemy_hit_flash > 0:
            enemy_hit_flash -= 1
        if poison_timer > 0:
            poison_timer -= 1
            if poison_timer % 60 == 0:
                player_hp -= 2
                battle_message = "Яд! (-2 HP)"
                if snd_poison and sound_cooldown == 0:
                    snd_poison.play()
                    sound_cooldown = 15

        if active_enemy["hp"] > 0:
            if is_mobile:
                if pygame.mouse.get_pressed()[0]:
                    mx, my = pygame.mouse.get_pos()
                    if mx < 400 and my > 300:
                        ariel_battle_rect.x -= battle_speed
                    elif mx > 400 and my > 300:
                        ariel_battle_rect.x += battle_speed
                    if my < 300:
                        ariel_battle_rect.y -= battle_speed
                    elif my > 500:
                        ariel_battle_rect.y += battle_speed
            else:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    ariel_battle_rect.x -= battle_speed
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    ariel_battle_rect.x += battle_speed
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    ariel_battle_rect.y -= battle_speed
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    ariel_battle_rect.y += battle_speed
            ariel_battle_rect.clamp_ip(box_rect)

            projectile_timer += 1
            if active_enemy["type"] == "shooter":
                if projectile_timer % 25 == 0:
                    projectiles.append(
                        {
                            "rect": pygame.Rect(
                                random.randint(box_rect.left, box_rect.right - 20),
                                box_rect.top,
                                20,
                                20,
                            ),
                            "vx": random.choice([-4, 4]),
                            "vy": 5,
                            "color": RED,
                        }
                    )
            elif active_enemy["type"] == "laser":
                if projectile_timer % 45 == 0:
                    projectiles.append(
                        {
                            "rect": pygame.Rect(
                                box_rect.left,
                                random.randint(box_rect.top, box_rect.bottom - 15),
                                15,
                                15,
                            ),
                            "vx": 7,
                            "vy": 0,
                            "color": PURPLE,
                        }
                    )
            elif active_enemy["type"] == "dual":
                if projectile_timer % 30 == 0:
                    py = random.randint(box_rect.top, box_rect.bottom - 20)
                    projectiles.append(
                        {
                            "rect": pygame.Rect(box_rect.left, py, 20, 20),
                            "vx": 6,
                            "vy": 0,
                            "color": (255, 150, 50),
                        }
                    )
                    projectiles.append(
                        {
                            "rect": pygame.Rect(box_rect.right - 20, py, 20, 20),
                            "vx": -6,
                            "vy": 0,
                            "color": (255, 150, 50),
                        }
                    )
            elif active_enemy["type"] == "poison":
                if projectile_timer % 25 == 0:
                    projectiles.append(
                        {
                            "rect": pygame.Rect(
                                random.randint(box_rect.left, box_rect.right - 20),
                                box_rect.top,
                                15,
                                15,
                            ),
                            "vx": random.choice([-4, 4]),
                            "vy": 5,
                            "color": POISON_COLOR,
                        }
                    )
            elif active_enemy["type"] == "boss":
                if projectile_timer % 15 == 0:
                    projectiles.append(
                        {
                            "rect": pygame.Rect(
                                random.randint(box_rect.left, box_rect.right - 20),
                                box_rect.top,
                                20,
                                20,
                            ),
                            "vx": random.choice([-4, 4]),
                            "vy": 7,
                            "color": RED,
                        }
                    )
                if projectile_timer % 40 == 0:
                    projectiles.append(
                        {
                            "rect": pygame.Rect(
                                box_rect.left,
                                random.randint(box_rect.top, box_rect.bottom - 15),
                                15,
                                15,
                            ),
                            "vx": 8,
                            "vy": 0,
                            "color": PURPLE,
                        }
                    )

        for proj in projectiles[:]:
            proj["rect"].x += proj["vx"]
            proj["rect"].y += proj["vy"]
            if (
                proj["rect"].right < box_rect.left
                or proj["rect"].left > box_rect.right
                or proj["rect"].bottom < box_rect.top
                or proj["rect"].top > box_rect.bottom
            ):
                projectiles.remove(proj)
            elif ariel_battle_rect.colliderect(proj["rect"]) and active_enemy["hp"] > 0:
                base_damage = 7 if active_enemy["type"] == "boss" else 5
                actual_damage = max(1, base_damage - 2) if has_armor else base_damage
                player_hp -= actual_damage
                battle_message = f"Урон! ({actual_damage} HP)"
                if active_enemy["type"] == "poison":
                    poison_timer = 180
                    battle_message = f"Яд! ({actual_damage} урона)"
                projectiles.remove(proj)
                shake_timer = 10
                ariel_flash_timer = 10
                if snd_hurt and sound_cooldown == 0:
                    snd_hurt.play()
                    sound_cooldown = 15

        if enemy_pulse > 0:
            enemy_pulse -= 1
        enemy_breath = math.sin(pygame.time.get_ticks() / 200) * 5

        if projectile_timer >= attack_duration or active_enemy["hp"] <= 0:
            if active_enemy["hp"] <= 0:
                projectiles.clear()
                current_state = STATE_WIN
                battle_message = "Победа! Нажми ENTER (или ТАП)"
                spawn_particles(400, 150, WHITE, 30)
                if snd_death and sound_cooldown == 0:
                    snd_death.play()
                    sound_cooldown = 30
                if active_enemy.get("drops_armor"):
                    has_armor = True
                    battle_message = "Броня Кота! (Урон снижен)"
            else:
                current_state = STATE_BATTLE
                battle_message = "Готов к бою!"
                reset_battle()

        if player_hp <= 0:
            current_state = STATE_DEAD
            play_menu_music()

    # --- ОТРИСОВКА ---
    render_surface = pygame.Surface((800, 600))

    if current_state == STATE_PLATFORM_SELECT:
        render_surface.fill(BLACK)
        title = title_font.render("ВЫБЕРИ ПЛАТФОРМУ", True, WHITE)
        render_surface.blit(title, title.get_rect(center=(400, 150)))
        pygame.draw.rect(
            render_surface, BTN_COLOR, (150, 250, 200, 80), border_radius=10
        )
        pygame.draw.rect(
            render_surface, WHITE, (150, 250, 200, 80), 2, border_radius=10
        )
        render_surface.blit(font.render("ПК (Клавиатура)", True, WHITE), (170, 275))
        pygame.draw.rect(
            render_surface, BTN_COLOR, (450, 250, 200, 80), border_radius=10
        )
        pygame.draw.rect(
            render_surface, WHITE, (450, 250, 200, 80), 2, border_radius=10
        )
        render_surface.blit(font.render("Телефон (Тапы)", True, WHITE), (470, 275))

    elif current_state == STATE_MENU:
        render_surface.fill(BLACK)
        for i in range(20):
            y = (pygame.time.get_ticks() // 10 + i * 30) % 600
            pygame.draw.rect(render_surface, (30, 0, 0), (0, y, 800, 2))
        title = title_font.render("ARIEL'S WORLD", True, RED)
        render_surface.blit(title, title.get_rect(center=(400, 200)))
        sub = font.render("Побег из мира компьютеров", True, WHITE)
        render_surface.blit(sub, sub.get_rect(center=(400, 270)))
        pulse = (math.sin(pygame.time.get_ticks() / 150) + 1) * 5
        start = font.render("НАЖМИ ENTER/ЭКРАН", True, YELLOW)
        render_surface.blit(start, start.get_rect(center=(400, 450 + pulse)))
        creds = small_font.render(
            "Создано Никитой (Камень Великий Второй)", True, (100, 100, 100)
        )
        render_surface.blit(creds, (20, 560))
        music_cred = small_font.render(
            "Композитор: Степан Друнишка", True, (150, 150, 150)
        )
        render_surface.blit(music_cred, music_cred.get_rect(bottomright=(780, 580)))

    elif current_state == STATE_DIALOGUE:
        render_surface.fill(BATTLE_BG)
        draw_ariel(render_surface, (100, 300, 100, 100), is_battle=True)
        if boss_to_fight:
            draw_enemy(
                render_surface, (500, 250, 100, 100), boss_to_fight["type"], 0, False
            )
        pygame.draw.rect(render_surface, BLACK, (50, 450, 700, 120))
        pygame.draw.rect(render_surface, WHITE, (50, 450, 700, 120), 2)
        msg = small_font.render(current_dialogue, True, WHITE)
        render_surface.blit(msg, (70, 480))
        if not is_mobile:
            render_surface.blit(
                small_font.render("Нажми ENTER...", True, YELLOW), (450, 540)
            )

    elif current_state == STATE_OVERWORLD:
        render_surface.fill((20, 20, 25))
        for i in range(0, 800, 40):
            pygame.draw.line(render_surface, (25, 25, 30), (i, 0), (i, 600))
        for i in range(0, 600, 40):
            pygame.draw.line(render_surface, (25, 25, 30), (0, i), (800, i))
        for wall in rooms[current_room]["walls"]:
            pygame.draw.rect(render_surface, WALL, (wall[0], wall[1], wall[2], wall[3]))
            pygame.draw.rect(
                render_surface, WALL_HIGHLIGHT, (wall[0], wall[1], wall[2], wall[3]), 2
            )
        for door in rooms[current_room]["doors"]:
            pygame.draw.rect(
                render_surface,
                door["color"],
                (door["rect"][0], door["rect"][1], door["rect"][2], door["rect"][3]),
            )
            pygame.draw.rect(
                render_surface,
                WHITE,
                (door["rect"][0], door["rect"][1], door["rect"][2], door["rect"][3]),
                2,
            )
        for enemy in rooms[current_room]["enemies"]:
            if enemy["hp"] > 0:
                draw_enemy(
                    render_surface,
                    (enemy["x"], enemy["y"], 40, 40),
                    enemy["type"],
                    0,
                    False,
                )
        attacking = (
            current_state == STATE_BATTLE or current_state == STATE_ATTACK
        ) and attack_anim_timer > 0
        draw_ariel(
            render_surface,
            (player_x, player_y, player_size, player_size),
            is_battle=False,
            attacking=attacking,
        )
        text = small_font.render(f"Комната {current_room + 1}.", True, WHITE)
        render_surface.blit(text, (20, 20))
        if has_armor:
            render_surface.blit(
                small_font.render("Броня: ЕСТЬ", True, ARMOR_COLOR), (20, 80)
            )
        if battle_message:
            msg = small_font.render(battle_message, True, YELLOW)
            render_surface.blit(msg, (20, 50))
            battle_message = ""
        if is_mobile:
            draw_mobile_buttons(render_surface, STATE_OVERWORLD)

    elif current_state in [STATE_BATTLE, STATE_ATTACK, STATE_WIN, STATE_TIMING]:
        render_surface.fill(BATTLE_BG)
        for i in range(0, 800, 40):
            pygame.draw.line(render_surface, (35, 35, 45), (i, 0), (i, 600))
        for i in range(0, 600, 40):
            pygame.draw.line(render_surface, (35, 35, 45), (0, i), (800, i))
        msg_text = font.render(battle_message, True, WHITE)
        render_surface.blit(msg_text, (50, 50))
        if active_enemy and active_enemy["hp"] > 0:
            size_offset = enemy_pulse if enemy_pulse > 0 else enemy_breath
            enemy_rect = pygame.Rect(
                350 - size_offset // 2,
                100 - size_offset // 2,
                100 + size_offset,
                100 + size_offset,
            )
            if enemy_hit_flash > 0:
                enemy_rect.x += random.randint(-5, 5)
                enemy_rect.y += random.randint(-5, 5)
            draw_enemy(
                render_surface, enemy_rect, active_enemy["type"], enemy_pulse, False
            )
            enemy_hp_text = small_font.render(
                f"{active_enemy['name']} HP: {active_enemy['hp']}", True, WHITE
            )
            render_surface.blit(enemy_hp_text, (350, 220))
        hp_text = font.render(f"HP: {player_hp}/{player_max_hp}", True, GREEN)
        render_surface.blit(hp_text, (650, 550))
        if has_armor:
            render_surface.blit(
                small_font.render("[БРОНЯ]", True, ARMOR_COLOR), (650, 520)
            )
        if poison_timer > 0:
            render_surface.blit(
                small_font.render("[ЯД]", True, POISON_COLOR), (650, 490)
            )
        pygame.draw.rect(render_surface, BOX_BORDER, box_rect, 2)
        if ariel_flash_timer > 0:
            ariel_color = FLASH_COLOR if ariel_flash_timer % 4 < 2 else RED
            ariel_flash_timer -= 1
            pygame.draw.rect(render_surface, ariel_color, ariel_battle_rect)
        else:
            draw_ariel(
                render_surface,
                (ariel_battle_rect.x, ariel_battle_rect.y, 20, 20),
                is_battle=True,
            )
        for proj in projectiles:
            pygame.draw.rect(render_surface, proj["color"], proj["rect"])
        for p in particles[:]:
            pygame.draw.rect(render_surface, p["color"], (p["x"], p["y"], 5, 5))
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["timer"] -= 1
            if p["timer"] <= 0:
                particles.remove(p)
        if current_state == STATE_TIMING:
            bar_rect = pygame.Rect(200, 350, 400, 20)
            pygame.draw.rect(render_surface, (50, 50, 50), bar_rect)
            pygame.draw.rect(render_surface, RED, (200, 350, 120, 20))
            pygame.draw.rect(render_surface, RED, (480, 350, 120, 20))
            pygame.draw.rect(render_surface, YELLOW, (320, 350, 40, 20))
            pygame.draw.rect(render_surface, YELLOW, (440, 350, 40, 20))
            pygame.draw.rect(render_surface, ORANGE, (360, 350, 80, 20))
            cursor_x = 200 + timing_cursor
            pygame.draw.rect(render_surface, WHITE, (cursor_x, 345, 10, 30))
            hint = small_font.render("ЖМИ ENTER/ЭКРАН!", True, WHITE)
            render_surface.blit(hint, (300, 400))
        elif current_state == STATE_BATTLE and active_enemy["hp"] > 0:
            if is_mobile:
                draw_mobile_buttons(render_surface, STATE_BATTLE)
            else:
                button_width = 150
                button_y = 520
                button_xs = [30, 210, 390, 570]
                for i, (option, x) in enumerate(zip(battle_options, button_xs)):
                    color = YELLOW if i == battle_selected else WHITE
                    pygame.draw.rect(
                        render_surface, color, (x, button_y, button_width, 40), 2
                    )
                    render_surface.blit(
                        small_font.render(option, True, color), (x + 20, button_y + 10)
                    )
        elif current_state == STATE_ATTACK:
            hint = small_font.render("УВОРАЧИВАЙСЯ!", True, YELLOW)
            render_surface.blit(hint, (320, 520))
        elif current_state == STATE_WIN:
            hint = small_font.render("ДАЛЕЕ...", True, YELLOW)
            render_surface.blit(hint, (320, 520))
        if is_mobile and current_state in [STATE_DIALOGUE, STATE_TIMING]:
            draw_mobile_buttons(render_surface, current_state)

    elif current_state == STATE_DEAD:
        render_surface.fill(DEATH_BG)
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        render_surface.blit(overlay, (0, 0))
        render_surface.blit(title_font.render("ТЫ ПАЛ", True, (200, 0, 0)), (250, 250))
        render_surface.blit(
            font.render("Ариэль не справился...", True, (150, 150, 150)), (250, 320)
        )
        pulse = (math.sin(pygame.time.get_ticks() / 150) + 1) * 5
        render_surface.blit(
            font.render("НАЖМИ ENTER/ЭКРАН", True, YELLOW), (220, 450 + pulse)
        )

    elif current_state == STATE_END_KILL:
        render_surface.fill((20, 0, 0))
        end_title_font = pygame.font.SysFont("Arial", 45, bold=True)
        win_text = end_title_font.render("КОНЦОВКА: ЖЕСТОКОСТЬ", True, (200, 0, 0))
        render_surface.blit(win_text, win_text.get_rect(center=(400, 200)))
        sub_text = font.render(
            "Ариэль уничтожил Робота Стёпу. Но какой ценой?", True, WHITE
        )
        render_surface.blit(sub_text, sub_text.get_rect(center=(400, 300)))
        sub_text2 = font.render(
            "Мир рухнул. Ариэль остался один.", True, (150, 150, 150)
        )
        render_surface.blit(sub_text2, sub_text2.get_rect(center=(400, 340)))
        pulse = (math.sin(pygame.time.get_ticks() / 150) + 1) * 5
        restart_text = font.render("НАЖМИ ENTER/ЭКРАН", True, YELLOW)
        render_surface.blit(
            restart_text, restart_text.get_rect(center=(400, 450 + pulse))
        )

    elif current_state == STATE_END_MERCY:
        render_surface.fill((10, 40, 20))
        end_title_font = pygame.font.SysFont("Arial", 45, bold=True)
        win_text = end_title_font.render("КОНЦОВКА: МИЛОСЕРДИЕ", True, GREEN)
        render_surface.blit(win_text, win_text.get_rect(center=(400, 200)))
        sub_text = font.render(
            "Ариэль взломал Робота Стёпу и снял блокировку.", True, WHITE
        )
        render_surface.blit(sub_text, sub_text.get_rect(center=(400, 300)))
        sub_text2 = font.render(
            "Теперь они вместе будут исследовать миры.", True, (150, 200, 150)
        )
        render_surface.blit(sub_text2, sub_text2.get_rect(center=(400, 340)))
        pulse = (math.sin(pygame.time.get_ticks() / 150) + 1) * 5
        restart_text = font.render("НАЖМИ ENTER/ЭКРАН", True, YELLOW)
        render_surface.blit(
            restart_text, restart_text.get_rect(center=(400, 450 + pulse))
        )

    screen.blit(render_surface, (shake_x, shake_y))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
