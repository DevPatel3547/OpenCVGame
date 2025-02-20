# engine/projectile.py
import pygame
from config import YELLOW, WORLD_WIDTH, WORLD_HEIGHT

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (5, 5), 5)
        self.rect = self.image.get_rect(center=pos)
        self.speed = 10
        self.direction = pygame.Vector2(0, -1)  # Projectile moves upward

    def update(self):
        self.rect.x += int(self.direction.x * self.speed)
        self.rect.y += int(self.direction.y * self.speed)
        # Remove projectile if it goes off-world.
        if (self.rect.bottom < 0 or self.rect.top > WORLD_HEIGHT or
            self.rect.right < 0 or self.rect.left > WORLD_WIDTH):
            self.kill()
