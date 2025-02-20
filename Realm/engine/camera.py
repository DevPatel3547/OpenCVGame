# engine/camera.py
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT

class Camera:
    def __init__(self):
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.offset = pygame.Vector2(0, 0)

    def update(self, target_rect):
        # Center the camera on the target while clamping to world bounds.
        x = target_rect.centerx - self.width // 2
        y = target_rect.centery - self.height // 2
        x = max(0, min(x, WORLD_WIDTH - self.width))
        y = max(0, min(y, WORLD_HEIGHT - self.height))
        self.offset = pygame.Vector2(x, y)
