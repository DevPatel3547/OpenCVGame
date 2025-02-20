# engine/enemy.py
import pygame
import random
from config import RED

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # Create a square enemy.
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=pos)
        self.speed = random.randint(1, 3)
        self.health = 50

    def update(self, player_rect):
        # Move toward the player.
        direction = pygame.Vector2(player_rect.center) - pygame.Vector2(self.rect.center)
        if direction.length() != 0:
            direction = direction.normalize() * self.speed
        self.rect.centerx += int(direction.x)
        self.rect.centery += int(direction.y)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()
