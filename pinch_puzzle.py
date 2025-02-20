import cv2
import mediapipe as mp
import pygame
import sys
import random
import numpy as np

# -------------------- SETUP FOR HAND DETECTION --------------------
mp_hands = mp.solutions.hands
# Initialize the Hands solution with one hand and a decent detection confidence
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# -------------------- INITIALIZE PYGAME --------------------
pygame.init()
width, height = 640, 480  # window size (and camera frame size)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pinch Puzzle Game")

# -------------------- LOAD AND SPLIT THE PUZZLE IMAGE --------------------
# Ensure you have a 'puzzle.jpg' in your directory. It will be scaled to the window size.
puzzle_img = pygame.image.load("puzzle.jpg")
puzzle_img = pygame.transform.scale(puzzle_img, (width, height))
piece_width = width // 2
piece_height = height // 2

# PuzzlePiece class to manage each piece
class PuzzlePiece:
    def __init__(self, image, target_pos, initial_pos):
        self.image = image
        self.target_pos = target_pos  # correct position on the board
        self.pos = list(initial_pos)  # current position (as a list so it can be modified)
        self.placed = False  # flag to indicate if the piece has been snapped into place
    
    def draw(self, surface):
        surface.blit(self.image, self.pos)
    
    def is_near_target(self):
        # Check if the current position is within 20 pixels of the target (both x and y)
        x, y = self.pos
        tx, ty = self.target_pos
        return abs(x - tx) < 20 and abs(y - ty) < 20

    def snap_to_target(self):
        self.pos = list(self.target_pos)
        self.placed = True

# Create target positions (for a 2x2 grid)
targets = []
for i in range(2):
    for j in range(2):
        targets.append((j * piece_width, i * piece_height))

# Extract puzzle pieces from the main image
piece_images = []
for i in range(2):
    for j in range(2):
        rect = pygame.Rect(j * piece_width, i * piece_height, piece_width, piece_height)
        piece_surface = pygame.Surface((piece_width, piece_height))
        piece_surface.blit(puzzle_img, (0, 0), rect)
        piece_images.append(piece_surface)

# Randomize initial positions for each piece (making sure they are within the window bounds)
initial_positions = []
for _ in targets:
    pos = (random.randint(0, width - piece_width), random.randint(0, height - piece_height))
    initial_positions.append(pos)

# Create a list of PuzzlePiece objects
pieces = []
for img, target, init in zip(piece_images, targets, initial_positions):
    pieces.append(PuzzlePiece(img, target, init))

# -------------------- SETUP FOR CAMERA INPUT --------------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

clock = pygame.time.Clock()

# Variables to keep track of the grabbed piece and pinch status
grabbed_piece = None
pinch_active = False

# -------------------- HELPER FUNCTIONS --------------------
def get_hand_landmarks(frame):
    """Process the frame to extract hand landmarks using Mediapipe."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    return results

def get_pinch_status(landmarks):
    """
    Determine the pinch distance (between thumb tip and index finger tip) 
    and return the index finger tip position (used as pointer).
    """
    if landmarks:
        thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        # Normalized coordinates (0 to 1)
        x1, y1 = thumb_tip.x, thumb_tip.y
        x2, y2 = index_tip.x, index_tip.y
        dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        # Convert the index finger tip to screen coordinates
        finger_pos = (int(index_tip.x * width), int(index_tip.y * height))
        return dist, finger_pos
    return None, (0, 0)

# -------------------- MAIN GAME LOOP --------------------
running = True
while running:
    # Process Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Capture frame from the webcam
    ret, frame = cap.read()
    if not ret:
        continue
    frame = cv2.flip(frame, 1)  # Flip horizontally for a mirror view

    # Process the frame with Mediapipe to detect hand landmarks
    results = get_hand_landmarks(frame)
    pinch_distance = None
    finger_pos = (0, 0)
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            pinch_distance, finger_pos = get_pinch_status(handLms)
            # (Optional) Draw landmarks on the frame for debugging:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

    # Determine if a pinch is active based on a chosen threshold (adjust if needed)
    if pinch_distance is not None and pinch_distance < 0.05:
        pinch_active = True
    else:
        pinch_active = False
        grabbed_piece = None  # release any grabbed piece if pinch is not active

    # If a pinch is active, check for interaction with puzzle pieces
    if pinch_active:
        # If no piece is currently grabbed, see if any piece is under the pointer
        if grabbed_piece is None:
            for piece in pieces:
                if not piece.placed:
                    px, py = piece.pos
                    if px < finger_pos[0] < px + piece_width and py < finger_pos[1] < py + piece_height:
                        grabbed_piece = piece
                        break
        # If a piece is grabbed, update its position to follow the finger
        if grabbed_piece:
            grabbed_piece.pos = [finger_pos[0] - piece_width // 2, finger_pos[1] - piece_height // 2]
    else:
        # When pinch is released, check if the grabbed piece is near its target position
        if grabbed_piece and not grabbed_piece.placed:
            if grabbed_piece.is_near_target():
                grabbed_piece.snap_to_target()
            grabbed_piece = None

    # -------------------- RENDERING --------------------
    # Clear the screen with a background color
    screen.fill((50, 50, 50))
    
    # (Optional) Display the camera feed in the top-left corner for reference.
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Rotate the frame so it displays correctly in Pygame
    frame_surface = pygame.surfarray.make_surface(np.rot90(frame_rgb))
    cam_feed_rect = frame_surface.get_rect(topleft=(0, 0))
    screen.blit(frame_surface, cam_feed_rect)
    
    # Draw all puzzle pieces
    for piece in pieces:
        piece.draw(screen)
    
    # Draw a circle at the finger position if a pinch is active (for visual feedback)
    if pinch_active:
        pygame.draw.circle(screen, (255, 0, 0), finger_pos, 10)
    
    pygame.display.flip()
    clock.tick(30)  # limit the loop to 30 frames per second

# -------------------- CLEANUP --------------------
cap.release()
pygame.quit()
sys.exit()
