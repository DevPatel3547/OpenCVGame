# config.py
import os

# Screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# World dimensions (in pixels)
WORLD_WIDTH = 2000
WORLD_HEIGHT = 2000

# Tile configuration
TILE_SIZE = 64
TILES_X = WORLD_WIDTH // TILE_SIZE
TILES_Y = WORLD_HEIGHT // TILE_SIZE

# Colors (RGB tuples)
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GRAY   = (100, 100, 100)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
BLUE   = (0, 0, 255)
YELLOW = (255, 255, 0)

# Tile types
TILE_GRASS = 0
TILE_WATER = 1
TILE_STONE = 2

TILE_COLORS = {
    TILE_GRASS: (34, 139, 34),   # Forest Green
    TILE_WATER: (0, 191, 255),   # Deep Sky Blue
    TILE_STONE: (169, 169, 169)  # Dark Gray
}

# Assets directories
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')
