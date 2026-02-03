print("🔥 NEW SPRITE VERSION RUNNING 🔥")

import pygame
import sys
import math
import random

pygame.init()

# ---------------- WINDOW ----------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top Down Shooter")
clock = pygame.time.Clock()

# ---------------- PLAYER ----------------
PLAYER_SIZE = 48
PLAYER_SPEED = 300

# ---------------- BULLETS ----------------
BULLET_SPEED = 600
BULLET_RADIUS = 4

# ---------------- ENEMIES ----------------
ENEMY_SIZE = 48
ENEMY_SPEED = 150
SPAWN_DELAY = 1.2

# ---------------- FONTS ----------------
font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 64)

# ---------------- LOAD IMAGES ----------------
player_img = pygame.image.load("assets/player_ship.png").convert_alpha()
enemy_img = pygame.image.load("assets/enemy_ship.png").convert_alpha()

player_img = pygame.transform.scale(player_img, (PLAYER_SIZE, PLAYER_SIZE))
enemy_img = pygame.transform.scale(enemy_img, (ENEMY_SIZE, ENEMY_SIZE))

# ---------------- RESET GAME ----------------
def reset_game():
    return {
        "player_x": WIDTH // 2,
        "player_y": HEIGHT // 2,
        "bullets": [],
        "enemies": [],
        "spawn_timer": 0,
        "score": 0,
        "game_over": False
    }

state = reset_game()

# ---------------- GAME LOOP ----------------
running = True
while running:
    dt = clock.tick(60) / 1000

    # -------- EVENTS --------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not state["game_over"]:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                dx = mx - (state["player_x"] + PLAYER_SIZE / 2)
                dy = my - (state["player_y"] + PLAYER_SIZE / 2)
                angle = math.atan2(dy, dx)

                state["bullets"].append({
                    "x": state["player_x"] + PLAYER_SIZE / 2,
                    "y": state["player_y"] + PLAYER_SIZE / 2,
                    "dx": math.cos(angle),
                    "dy": math.sin(angle)
                })

        if state["game_over"]:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                state = reset_game()

    # -------- GAME LOGIC --------
    if not state["game_over"]:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            state["player_y"] -= PLAYER_SPEED * dt
        if keys[pygame.K_s]:
            state["player_y"] += PLAYER_SPEED * dt
        if keys[pygame.K_a]:
            state["player_x"] -= PLAYER_SPEED * dt
        if keys[pygame.K_d]:
            state["player_x"] += PLAYER_SPEED * dt

        # Boundaries
        state["player_x"] = max(0, min(state["player_x"], WIDTH - PLAYER_SIZE))
        state["player_y"] = max(0, min(state["player_y"], HEIGHT - PLAYER_SIZE))

        # Bullets update
        for bullet in state["bullets"][:]:
            bullet["x"] += bullet["dx"] * BULLET_SPEED * dt
            bullet["y"] += bullet["dy"] * BULLET_SPEED * dt

            if bullet["x"] < 0 or bullet["x"] > WIDTH or bullet["y"] < 0 or bullet["y"] > HEIGHT:
                state["bullets"].remove(bullet)

        # Enemy spawn
        state["spawn_timer"] += dt
        if state["spawn_timer"] >= SPAWN_DELAY:
            state["spawn_timer"] = 0
            side = random.choice(["top", "bottom", "left", "right"])

            if side == "top":
                ex, ey = random.randint(0, WIDTH), -ENEMY_SIZE
            elif side == "bottom":
                ex, ey = random.randint(0, WIDTH), HEIGHT + ENEMY_SIZE
            elif side == "left":
                ex, ey = -ENEMY_SIZE, random.randint(0, HEIGHT)
            else:
                ex, ey = WIDTH + ENEMY_SIZE, random.randint(0, HEIGHT)

            state["enemies"].append({"x": ex, "y": ey})

        # Enemy movement
        for enemy in state["enemies"]:
            dx = (state["player_x"] + PLAYER_SIZE / 2) - enemy["x"]
            dy = (state["player_y"] + PLAYER_SIZE / 2) - enemy["y"]
            dist = math.hypot(dx, dy)

            if dist != 0:
                enemy["x"] += (dx / dist) * ENEMY_SPEED * dt
                enemy["y"] += (dy / dist) * ENEMY_SPEED * dt

        # Collisions
        player_rect = pygame.Rect(
            state["player_x"], state["player_y"], PLAYER_SIZE, PLAYER_SIZE
        )

        for enemy in state["enemies"][:]:
            enemy_rect = pygame.Rect(enemy["x"], enemy["y"], ENEMY_SIZE, ENEMY_SIZE)

            if enemy_rect.colliderect(player_rect):
                state["game_over"] = True

            for bullet in state["bullets"][:]:
                bullet_rect = pygame.Rect(
                    bullet["x"], bullet["y"],
                    BULLET_RADIUS * 2, BULLET_RADIUS * 2
                )

                if enemy_rect.colliderect(bullet_rect):
                    state["enemies"].remove(enemy)
                    state["bullets"].remove(bullet)
                    state["score"] += 1
                    break

    # -------- DRAW --------
    screen.fill((8, 8, 20))

    # Player sprite
    screen.blit(player_img, (state["player_x"], state["player_y"]))

    # Enemy sprites
    for enemy in state["enemies"]:
        screen.blit(enemy_img, (enemy["x"], enemy["y"]))

    # Bullets
    for bullet in state["bullets"]:
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (int(bullet["x"]), int(bullet["y"])),
            BULLET_RADIUS
        )

    # Score
    score_text = font.render(f"Score: {state['score']}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # Game Over UI
    if state["game_over"]:
        over = big_font.render("GAME OVER", True, (255, 80, 80))
        replay = font.render("Press R to Replay", True, (200, 200, 200))
        screen.blit(over, (WIDTH//2 - over.get_width()//2, HEIGHT//2 - 50))
        screen.blit(replay, (WIDTH//2 - replay.get_width()//2, HEIGHT//2 + 10))

    pygame.display.update()

pygame.quit()
sys.exit()


