# engine/world.py
import pygame
import random
from config import TILE_SIZE, TILES_X, TILES_Y, TILE_COLORS, TILE_GRASS, TILE_WATER, TILE_STONE, BLACK

class World:
    def __init__(self):
        # Generate a random tile map.
        self.map = [[random.choice([TILE_GRASS, TILE_WATER, TILE_STONE]) for _ in range(TILES_X)]
                    for _ in range(TILES_Y)]

    def draw(self, surface, camera_offset):
        # Calculate visible tiles (ensure indices are integers)
        start_x = max(0, int(camera_offset.x // TILE_SIZE))
        start_y = max(0, int(camera_offset.y // TILE_SIZE))
        end_x = min(TILES_X, int((camera_offset.x + surface.get_width()) // TILE_SIZE) + 1)
        end_y = min(TILES_Y, int((camera_offset.y + surface.get_height()) // TILE_SIZE) + 1)
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.map[y][x]
                color = TILE_COLORS[tile]
                rect = pygame.Rect(x * TILE_SIZE - int(camera_offset.x), 
                                   y * TILE_SIZE - int(camera_offset.y),
                                   TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, BLACK, rect, 1)  # Draw tile border
