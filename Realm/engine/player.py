# engine/player.py
import pygame
import time
from config import BLUE, WORLD_WIDTH, WORLD_HEIGHT

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # Create a circular player sprite.
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLUE, (25, 25), 25)
        self.rect = self.image.get_rect(center=pos)
        self.speed = 5
        self.health = 100
        self.last_attack_time = 0
        self.attack_cooldown = 0.5  # seconds between attacks

    def update(self, target_pos):
        # Smoothly move toward the target position.
        direction = pygame.Vector2(target_pos) - pygame.Vector2(self.rect.center)
        if direction.length() > self.speed:
            direction = direction.normalize() * self.speed
        self.rect.centerx += int(direction.x)
        self.rect.centery += int(direction.y)

        # Clamp the player within world bounds.
        self.rect.left = max(self.rect.left, 0)
        self.rect.top = max(self.rect.top, 0)
        self.rect.right = min(self.rect.right, WORLD_WIDTH)
        self.rect.bottom = min(self.rect.bottom, WORLD_HEIGHT)

    def can_attack(self):
        return time.time() - self.last_attack_time > self.attack_cooldown

    def attack(self):
        self.last_attack_time = time.time()
        from engine.projectile import Projectile  # Import here to avoid circular dependencies
        return Projectile(self.rect.center)
