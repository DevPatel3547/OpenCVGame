import cv2
import mediapipe as mp
import pygame
import sys
import random
import numpy as np
import time

# -------------------- SETUP: Mediapipe & Constants --------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Define some colors
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
YELLOW = (255, 255, 0)

# -------------------- GAME OBJECT CLASSES --------------------
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # Create a transparent surface for the spaceship
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        # Draw a green triangle (pointing upward)
        pygame.draw.polygon(self.image, GREEN, [(25, 0), (0, 50), (50, 50)])
        self.rect = self.image.get_rect(center=pos)
    
    def update(self, pos):
        # Update spaceship position to follow the provided coordinates
        self.rect.center = pos
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=pos)
        self.speed = -10  # move upward
    
    def update(self):
        self.rect.y += self.speed
        # Remove bullet if it goes off-screen
        if self.rect.bottom < 0:
            self.kill()
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, speed):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
    
    def update(self):
        self.rect.y += self.speed
        # Remove enemy if it goes off-screen
        if self.rect.top > 600:
            self.kill()
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)

# -------------------- MAIN GAME CLASS --------------------
class SpaceGestureShooter:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Space Gesture Shooter")
        self.clock = pygame.time.Clock()
        
        # Load fonts for UI
        self.font_large = pygame.font.SysFont("Arial", 48)
        self.font_small = pygame.font.SysFont("Arial", 24)
        
        # Define game states: "MENU", "GAME", "GAMEOVER"
        self.state = "MENU"
        
        # Setup the webcam
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        # Initialize game objects
        self.spaceship = Spaceship((self.width//2, self.height - 50))
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.last_shot_time = 0
        self.shot_cooldown = 0.3  # seconds between shots
        self.last_enemy_spawn = time.time()
        self.enemy_spawn_interval = 1.0  # spawn an enemy every 1 second
        self.score = 0
        
        # Create a starfield background (list of [x, y] positions)
        self.stars = [[random.randint(0, self.width), random.randint(0, self.height)] for _ in range(100)]
    
    def run(self):
        while True:
            if self.state == "MENU":
                self.menu_loop()
            elif self.state == "GAME":
                self.game_loop()
            elif self.state == "GAMEOVER":
                self.game_over_loop()
    
    def menu_loop(self):
        # Main menu loop
        while self.state == "MENU":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.state = "GAME"
            
            self.screen.fill(BLACK)
            title_text = self.font_large.render("Space Gesture Shooter", True, WHITE)
            instr_text = self.font_small.render("Move your finger to steer. Pinch to shoot. Press ENTER to start.", True, WHITE)
            self.screen.blit(title_text, ((self.width - title_text.get_width()) // 2, self.height // 3))
            self.screen.blit(instr_text, ((self.width - instr_text.get_width()) // 2, self.height // 2))
            pygame.display.flip()
            self.clock.tick(30)
    
    def game_loop(self):
        # Reset objects for a new game
        self.spaceship = Spaceship((self.width//2, self.height - 50))
        self.bullets.empty()
        self.enemies.empty()
        self.score = 0
        self.last_shot_time = 0
        self.last_enemy_spawn = time.time()
        game_over = False
        
        while self.state == "GAME":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
            
            # Capture a frame from the webcam
            ret, frame = self.cap.read()
            if not ret:
                continue
            frame = cv2.flip(frame, 1)  # Mirror view
            results = self.get_hand_landmarks(frame)
            pinch_distance, finger_pos = None, (self.width // 2, self.height // 2)
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    pinch_distance, finger_pos = self.get_pinch_status(handLms)
                    # Optionally, draw landmarks on the frame for debugging:
                    mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            
            # Update spaceship position based on finger position from camera
            self.spaceship.update(finger_pos)
            
            # Fire a bullet if a pinch gesture is detected and cooldown has passed
            current_time = time.time()
            if pinch_distance is not None and pinch_distance < 0.05:
                if current_time - self.last_shot_time > self.shot_cooldown:
                    bullet = Bullet(self.spaceship.rect.midtop)
                    self.bullets.add(bullet)
                    self.last_shot_time = current_time
            
            # Update bullets and enemy positions
            self.bullets.update()
            self.enemies.update()
            
            # Spawn new enemies at intervals
            if current_time - self.last_enemy_spawn > self.enemy_spawn_interval:
                enemy_x = random.randint(20, self.width - 20)
                enemy = Enemy((enemy_x, -20), random.randint(2, 5))
                self.enemies.add(enemy)
                self.last_enemy_spawn = current_time
            
            # Check for bullet-enemy collisions
            for bullet in self.bullets:
                hit_enemies = pygame.sprite.spritecollide(bullet, self.enemies, True)
                if hit_enemies:
                    bullet.kill()
                    self.score += 10
            
            # Check if an enemy collides with the spaceship
            if pygame.sprite.spritecollide(self.spaceship, self.enemies, False):
                game_over = True
            
            if game_over:
                self.state = "GAMEOVER"
            
            # Update starfield background (stars moving downward)
            for star in self.stars:
                star[1] += 1
                if star[1] > self.height:
                    star[0] = random.randint(0, self.width)
                    star[1] = 0
            
            # -------------------- RENDERING --------------------
            self.screen.fill(BLACK)
            # Draw stars
            for star in self.stars:
                pygame.draw.circle(self.screen, WHITE, star, 2)
            
            # Draw game objects
            self.spaceship.draw(self.screen)
            for bullet in self.bullets:
                bullet.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            # Display current score
            score_text = self.font_small.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            
            # Show a small thumbnail of the camera feed in the corner
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(np.rot90(frame_rgb))
            thumb = pygame.transform.scale(frame_surface, (160, 120))
            self.screen.blit(thumb, (self.width - 170, 10))
            
            # Draw a red circle as a visual indicator if pinching
            if pinch_distance is not None and pinch_distance < 0.05:
                pygame.draw.circle(self.screen, RED, finger_pos, 15)
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def game_over_loop(self):
        # Display game-over screen with final score and restart prompt
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
            self.screen.blit(over_text, ((self.width - over_text.get_width()) // 2, self.height // 3))
            self.screen.blit(score_text, ((self.width - score_text.get_width()) // 2, self.height // 2))
            self.screen.blit(instr_text, ((self.width - instr_text.get_width()) // 2, self.height // 2 + 40))
            pygame.display.flip()
            self.clock.tick(30)
    
    def get_hand_landmarks(self, frame):
        # Process the camera frame for hand landmarks using Mediapipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        return results
    
    def get_pinch_status(self, landmarks):
        # Calculate distance between thumb tip and index finger tip to determine a pinch
        thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        x1, y1 = thumb_tip.x, thumb_tip.y
        x2, y2 = index_tip.x, index_tip.y
        dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        # Convert the index tip coordinates to screen space
        finger_pos = (int(index_tip.x * self.width), int(index_tip.y * self.height))
        return dist, finger_pos
    
    def cleanup(self):
        self.cap.release()
        pygame.quit()
        sys.exit()

# -------------------- ENTRY POINT --------------------
if __name__ == "__main__":
    game = SpaceGestureShooter()
    game.run()
