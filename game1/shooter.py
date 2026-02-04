import pygame
import random
import sys
import math

pygame.init()
pygame.mixer.init()

# ---------------- WINDOW ----------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top Down Shooter")
clock = pygame.time.Clock()

# ---------------- PLAYER ----------------
PLAYER_SIZE = 48
PLAYER_SPEED = 300
PLAYER_MAX_HP = 5

# ---------------- BULLETS ----------------
BULLET_SPEED = 600
BULLET_RADIUS = 4
FIRE_COOLDOWN = 250  # ms

# ---------------- ENEMIES ----------------
ENEMY_SIZE = 48
ENEMY_SPEED = 150
SPAWN_DELAY = 1.2
BOSS_TRIGGER_SCORE = 15

# ---------------- BOSS ----------------
BOSS_SIZE = 120
BOSS_SPEED = 80
BOSS_MAX_HP = 60
BOSS_FIRE_DELAY = 1000
BOSS_BULLET_SPEED = 300

# ---------------- EFFECTS ----------------
SHAKE_DURATION = 0.15
SHAKE_INTENSITY = 6
FLASH_DURATION = 0.12   # only player flash

# ---------------- FONTS ----------------
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 64)

# ---------------- LOAD IMAGES ----------------
def load_image(path, size):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size)

player_img = load_image("assets/player_ship.png", (PLAYER_SIZE, PLAYER_SIZE))
enemy_img  = load_image("assets/enemy_ship.png", (ENEMY_SIZE, ENEMY_SIZE))
boss_img   = load_image("assets/boss_ship.png",  (BOSS_SIZE, BOSS_SIZE))

# ---------------- LOAD AUDIO ----------------
game_over_sound = pygame.mixer.Sound("assets/game_over.wav")

# ---------------- RESET GAME ----------------
def reset_game():
    return {
        "player_x": WIDTH // 2,
        "player_y": HEIGHT - 80,
        "player_hp": PLAYER_MAX_HP,

        "bullets": [],
        "enemies": [],
        "boss_bullets": [],

        "spawn_timer": 0,
        "last_shot": 0,
        "score": 0,

        "boss_active": False,
        "boss_hp": BOSS_MAX_HP,
        "boss_x": WIDTH // 2 - BOSS_SIZE // 2,
        "boss_y": -150,
        "boss_dir": 1,
        "boss_last_shot": 0,

        "shake": 0,
        "player_flash": 0,

        "game_over": False,
        "win": False,
        "sound_played": False
    }

state = reset_game()

# ---------------- GAME LOOP ----------------
running = True
while running:
    dt = clock.tick(60) / 1000
    now = pygame.time.get_ticks()

    # -------- EVENTS --------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if state["game_over"] and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                state = reset_game()

    keys = pygame.key.get_pressed()

    # -------- PLAYER MOVE --------
    if not state["game_over"]:
        if keys[pygame.K_w]:
            state["player_y"] -= PLAYER_SPEED * dt
        if keys[pygame.K_s]:
            state["player_y"] += PLAYER_SPEED * dt
        if keys[pygame.K_a]:
            state["player_x"] -= PLAYER_SPEED * dt
        if keys[pygame.K_d]:
            state["player_x"] += PLAYER_SPEED * dt

    state["player_x"] = max(0, min(WIDTH - PLAYER_SIZE, state["player_x"]))
    state["player_y"] = max(0, min(HEIGHT - PLAYER_SIZE, state["player_y"]))

    # -------- PLAYER SHOOT --------
    if (
        not state["game_over"]
        and keys[pygame.K_SPACE]
        and now - state["last_shot"] >= FIRE_COOLDOWN
    ):
        state["bullets"].append({
            "x": state["player_x"] + PLAYER_SIZE // 2,
            "y": state["player_y"]
        })
        state["last_shot"] = now

    # -------- PLAYER BULLETS --------
    for bullet in state["bullets"][:]:
        bullet["y"] -= BULLET_SPEED * dt
        if bullet["y"] < 0:
            state["bullets"].remove(bullet)

    # -------- ENEMY SPAWN (INFINITE) --------
    if not state["boss_active"]:
        state["spawn_timer"] += dt
        if state["spawn_timer"] >= SPAWN_DELAY:
            state["spawn_timer"] = 0
            state["enemies"].append({
                "x": random.randint(0, WIDTH - ENEMY_SIZE),
                "y": -ENEMY_SIZE
            })

    # -------- ENEMY MOVE --------
    for enemy in state["enemies"]:
        enemy["y"] += ENEMY_SPEED * dt

    player_rect = pygame.Rect(
        state["player_x"], state["player_y"],
        PLAYER_SIZE, PLAYER_SIZE
    )

    # -------- ENEMY COLLISIONS --------
    for enemy in state["enemies"][:]:
        enemy_rect = pygame.Rect(enemy["x"], enemy["y"], ENEMY_SIZE, ENEMY_SIZE)

        if enemy_rect.colliderect(player_rect):
            state["player_hp"] -= 1
            state["shake"] = SHAKE_DURATION
            state["player_flash"] = FLASH_DURATION
            state["enemies"].remove(enemy)

        for bullet in state["bullets"][:]:
            bullet_rect = pygame.Rect(bullet["x"], bullet["y"], 6, 6)
            if enemy_rect.colliderect(bullet_rect):
                state["enemies"].remove(enemy)
                state["bullets"].remove(bullet)
                state["score"] += 1
                state["shake"] = SHAKE_DURATION
                break

    # -------- SPAWN BOSS --------
    if state["score"] >= BOSS_TRIGGER_SCORE and not state["boss_active"]:
        state["boss_active"] = True
        state["enemies"].clear()

    # -------- BOSS LOGIC --------
    if state["boss_active"] and not state["game_over"]:
        if state["boss_y"] < 60:
            state["boss_y"] += BOSS_SPEED * dt

        state["boss_x"] += state["boss_dir"] * 140 * dt
        if state["boss_x"] <= 0 or state["boss_x"] >= WIDTH - BOSS_SIZE:
            state["boss_dir"] *= -1

        boss_rect = pygame.Rect(
            state["boss_x"], state["boss_y"],
            BOSS_SIZE, BOSS_SIZE
        )

        if now - state["boss_last_shot"] >= BOSS_FIRE_DELAY:
            dx = (state["player_x"] + PLAYER_SIZE / 2) - (state["boss_x"] + BOSS_SIZE / 2)
            dy = (state["player_y"] + PLAYER_SIZE / 2) - (state["boss_y"] + BOSS_SIZE / 2)
            dist = math.hypot(dx, dy)
            if dist != 0:
                state["boss_bullets"].append({
                    "x": state["boss_x"] + BOSS_SIZE / 2,
                    "y": state["boss_y"] + BOSS_SIZE / 2,
                    "dx": dx / dist,
                    "dy": dy / dist
                })
            state["boss_last_shot"] = now

        for b in state["boss_bullets"][:]:
            b["x"] += b["dx"] * BOSS_BULLET_SPEED * dt
            b["y"] += b["dy"] * BOSS_BULLET_SPEED * dt

            bullet_rect = pygame.Rect(b["x"], b["y"], 6, 6)
            if bullet_rect.colliderect(player_rect):
                state["player_hp"] -= 1
                state["shake"] = SHAKE_DURATION
                state["player_flash"] = FLASH_DURATION
                state["boss_bullets"].remove(b)

            if b["x"] < 0 or b["x"] > WIDTH or b["y"] < 0 or b["y"] > HEIGHT:
                state["boss_bullets"].remove(b)

        for bullet in state["bullets"][:]:
            bullet_rect = pygame.Rect(bullet["x"], bullet["y"], 6, 6)
            if boss_rect.colliderect(bullet_rect):
                state["boss_hp"] -= 1
                state["bullets"].remove(bullet)
                state["shake"] = SHAKE_DURATION
                if state["boss_hp"] <= 0:
                    state["win"] = True
                    state["game_over"] = True

    # -------- PLAYER DEAD --------
    if state["player_hp"] <= 0:
        state["game_over"] = True

    # -------- PLAY SOUND ONCE (WIN OR LOSE) --------
    if state["game_over"] and not state["sound_played"]:
        game_over_sound.play()
        state["sound_played"] = True

    # -------- EFFECT TIMERS --------
    state["shake"] = max(0, state["shake"] - dt)
    state["player_flash"] = max(0, state["player_flash"] - dt)

    # -------- SCREEN SHAKE --------
    ox = oy = 0
    if state["shake"] > 0:
        ox = random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)
        oy = random.randint(-SHAKE_INTENSITY, SHAKE_INTENSITY)

    # -------- DRAW --------
    screen.fill((10, 10, 30))

    screen.blit(player_img, (state["player_x"] + ox, state["player_y"] + oy))

    for enemy in state["enemies"]:
        screen.blit(enemy_img, (enemy["x"] + ox, enemy["y"] + oy))

    for bullet in state["bullets"]:
        pygame.draw.circle(screen, (255,255,255),
                           (int(bullet["x"] + ox), int(bullet["y"] + oy)), 4)

    for b in state["boss_bullets"]:
        pygame.draw.circle(screen, (255,60,60),
                           (int(b["x"] + ox), int(b["y"] + oy)), 5)

    if state["boss_active"]:
        screen.blit(boss_img, (state["boss_x"] + ox, state["boss_y"] + oy))
        pygame.draw.rect(screen, (255,0,0), (200, 20, 400, 16))
        pygame.draw.rect(
            screen, (0,255,0),
            (200, 20, 400 * (state["boss_hp"] / BOSS_MAX_HP), 16)
        )

    # -------- PLAYER FLASH --------
    if state["player_flash"] > 0:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 50, 50, 60))
        screen.blit(overlay, (0, 0))

    # -------- UI --------
    screen.blit(font.render(f"Score: {state['score']}", True, (255,255,255)), (10, 10))
    screen.blit(font.render(f"HP: {state['player_hp']}", True, (255,80,80)), (10, 32))

    if state["game_over"]:
        msg = "YOU WIN!" if state["win"] else "GAME OVER"
        text = big_font.render(msg, True, (255,80,80))
        restart = font.render("Press R to Restart", True, (220,220,220))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 40))
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 20))

    pygame.display.update()
