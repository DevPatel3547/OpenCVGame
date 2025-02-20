# engine/game.py
import cv2
import pygame
import sys
import time
import random
import numpy as np

from config import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT, BLACK, WHITE, RED
from engine.camera import Camera
from engine.world import World
from engine.player import Player
from engine.enemy import Enemy
from engine.projectile import Projectile
from utils import gesture

class RealmOfGesturesGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Realm of Gestures: Odyssey")
        self.clock = pygame.time.Clock()

        # Set up camera input (OpenCV)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_HEIGHT)

        # Game states: "MENU", "GAME", "GAMEOVER"
        self.state = "MENU"

        # Initialize game world, camera, and objects.
        self.world = World()
        self.camera = Camera()
        self.player = Player((WORLD_WIDTH // 2, WORLD_HEIGHT // 2))
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.last_enemy_spawn = time.time()
        self.enemy_spawn_interval = 2  # seconds

        # HUD and score.
        self.score = 0
        self.font_large = pygame.font.SysFont("Arial", 48)
        self.font_small = pygame.font.SysFont("Arial", 24)

    def run(self):
        while True:
            if self.state == "MENU":
                self.menu_loop()
            elif self.state == "GAME":
                self.game_loop()
            elif self.state == "GAMEOVER":
                self.game_over_loop()

    def menu_loop(self):
        while self.state == "MENU":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.state = "GAME"

            self.screen.fill(BLACK)
            title_text = self.font_large.render("Realm of Gestures: Odyssey", True, WHITE)
            instr_text = self.font_small.render("Use your hand to move, pinch to attack. Press ENTER to start.", True, WHITE)
            self.screen.blit(title_text, ((SCREEN_WIDTH - title_text.get_width()) // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(instr_text, ((SCREEN_WIDTH - instr_text.get_width()) // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            self.clock.tick(30)

    def game_loop(self):
        # Reset state for a new game.
        self.player.rect.center = (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        self.enemies.empty()
        self.projectiles.empty()
        self.score = 0
        self.player.health = 100

        game_over = False
        while self.state == "GAME":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()

            # Capture camera frame and process gesture input.
            ret, frame = self.cap.read()
            if not ret:
                continue
            frame = cv2.flip(frame, 1)
            results = gesture.get_hand_landmarks(frame)
            pinch_distance, finger_pos = None, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    pinch_distance, finger_pos = gesture.get_pinch_status(handLms)
                    # Optionally, landmarks can be drawn here if desired.

            # Map screen gesture to world space.
            world_target = (finger_pos[0] + self.camera.offset.x, finger_pos[1] + self.camera.offset.y)
            self.player.update(world_target)

            # Attack if pinch gesture is detected and cooldown allows.
            if pinch_distance is not None and pinch_distance < 0.05 and self.player.can_attack():
                proj = self.player.attack()
                self.projectiles.add(proj)

            # Spawn enemies periodically.
            current_time = time.time()
            if current_time - self.last_enemy_spawn > self.enemy_spawn_interval:
                spawn_x = random.randint(0, WORLD_WIDTH)
                spawn_y = random.choice([0, WORLD_HEIGHT])
                enemy = Enemy((spawn_x, spawn_y))
                self.enemies.add(enemy)
                self.last_enemy_spawn = current_time

            # Update enemies and check collisions with the player.
            for enemy in self.enemies:
                enemy.update(self.player.rect)
                if enemy.rect.colliderect(self.player.rect):
                    self.player.health -= 10
                    enemy.kill()
                    if self.player.health <= 0:
                        game_over = True

            self.projectiles.update()
            for projectile in self.projectiles:
                hits = pygame.sprite.spritecollide(projectile, self.enemies, False)
                for enemy in hits:
                    enemy.take_damage(25)
                    projectile.kill()
                    if not enemy.alive():
                        self.score += 50

            # Update camera to follow the player.
            self.camera.update(self.player.rect)

            # -------------------- RENDERING --------------------
            self.screen.fill(BLACK)
            self.world.draw(self.screen, self.camera.offset)
            for enemy in self.enemies:
                self.screen.blit(enemy.image, enemy.rect.topleft - self.camera.offset)
            for projectile in self.projectiles:
                self.screen.blit(projectile.image, projectile.rect.topleft - self.camera.offset)
            self.screen.blit(self.player.image, self.player.rect.topleft - self.camera.offset)

            # HUD: Score and Health.
            score_text = self.font_small.render(f"Score: {self.score}", True, WHITE)
            health_text = self.font_small.render(f"Health: {self.player.health}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(health_text, (10, 40))

            # Display a thumbnail of the camera feed.
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(np.rot90(frame_rgb))
            thumb = pygame.transform.scale(frame_surface, (200, 150))
            self.screen.blit(thumb, (SCREEN_WIDTH - 210, 10))

            # Visual indicator for pinch gesture.
            if pinch_distance is not None and pinch_distance < 0.05:
                pygame.draw.circle(self.screen, RED, finger_pos, 15)

            pygame.display.flip()
            self.clock.tick(60)

            if game_over:
                self.state = "GAMEOVER"

    def game_over_loop(self):
        while self.state == "GAMEOVER":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.state = "MENU"
            self.screen.fill(BLACK)
            over_text = self.font_large.render("GAME OVER", True, RED)
            score_text = self.font_small.render(f"Final Score: {self.score}", True, WHITE)
            instr_text = self.font_small.render("Press ENTER to return to menu", True, WHITE)
            self.screen.blit(over_text, ((SCREEN_WIDTH - over_text.get_width()) // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(score_text, ((SCREEN_WIDTH - score_text.get_width()) // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(instr_text, ((SCREEN_WIDTH - instr_text.get_width()) // 2, SCREEN_HEIGHT // 2 + 40))
            pygame.display.flip()
            self.clock.tick(30)

    def cleanup(self):
        self.cap.release()
        pygame.quit()
        sys.exit()
