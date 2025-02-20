import cv2
import mediapipe as mp
import pygame
import sys
import random
import numpy as np
import time

# -------------------- SETUP: Mediapipe Hand Detection --------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# -------------------- PUZZLE PIECE CLASS --------------------
class PuzzlePiece(pygame.sprite.Sprite):
    def __init__(self, image, target_pos, init_pos):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=init_pos)
        self.target_pos = target_pos
        self.placed = False

    def update(self):
        # If the piece is within 20 pixels of its target, snap it in place
        if not self.placed:
            tx, ty = self.target_pos
            if abs(self.rect.x - tx) < 20 and abs(self.rect.y - ty) < 20:
                self.rect.topleft = self.target_pos
                self.placed = True

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# -------------------- GAME CLASS WITH MULTIPLE STATES --------------------
class PinchPuzzleDeluxe:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        self.width, self.height = 800, 600  # Increased resolution for better visuals
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pinch Puzzle Deluxe")
        self.clock = pygame.time.Clock()

        # Define game states: MENU, GAME, and WIN
        self.state = "MENU"

        # Load assets
        # Background image (optional). If not found, we use a solid color.
        try:
            self.background = pygame.image.load("background.jpg")
            self.background = pygame.transform.scale(self.background, (self.width, self.height))
        except Exception as e:
            print("Background image not found, using solid background color.")
            self.background = None

        # Load the puzzle image (or generate a placeholder if not found)
        try:
            self.puzzle_image = pygame.image.load("puzzle.jpg")
            self.puzzle_image = pygame.transform.scale(self.puzzle_image, (self.width, self.height))
        except Exception as e:
            print("Puzzle image not found, generating a placeholder.")
            self.puzzle_image = pygame.Surface((self.width, self.height))
            self.puzzle_image.fill((200, 200, 200))

        # Puzzle configuration: create a 3x3 grid for extra challenge
        self.rows = 3
        self.cols = 3
        self.piece_width = self.width // self.cols
        self.piece_height = self.height // self.rows

        # Create a sprite group to hold all puzzle pieces
        self.pieces = pygame.sprite.Group()
        self.create_puzzle_pieces()

        # Setup the camera (make sure your webcam is available)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        # Variables to track gesture and piece dragging
        self.grabbed_piece = None
        self.pinch_active = False

    def create_puzzle_pieces(self):
        # Clear any existing pieces and split the puzzle image into pieces
        self.pieces.empty()
        for i in range(self.rows):
            for j in range(self.cols):
                # Define the rectangle for this piece
                rect = pygame.Rect(j * self.piece_width, i * self.piece_height, self.piece_width, self.piece_height)
                piece_image = pygame.Surface((self.piece_width, self.piece_height))
                piece_image.blit(self.puzzle_image, (0, 0), rect)
                target_pos = (j * self.piece_width, i * self.piece_height)
                # Randomize the starting position within screen bounds
                init_x = random.randint(0, self.width - self.piece_width)
                init_y = random.randint(0, self.height - self.piece_height)
                piece = PuzzlePiece(piece_image, target_pos, (init_x, init_y))
                self.pieces.add(piece)

    def get_hand_landmarks(self, frame):
        # Convert frame to RGB for Mediapipe processing
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        return results

    def get_pinch_status(self, landmarks):
        # Use Mediapipe landmarks to detect pinch (thumb tip and index finger tip)
        if landmarks:
            thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            # Calculate Euclidean distance between the two points
            x1, y1 = thumb_tip.x, thumb_tip.y
            x2, y2 = index_tip.x, index_tip.y
            dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            # Convert the index tip to screen coordinates
            finger_pos = (int(index_tip.x * self.width), int(index_tip.y * self.height))
            return dist, finger_pos
        return None, (0, 0)

    def run(self):
        # Main loop that switches between menu, game, and win states
        while True:
            if self.state == "MENU":
                self.menu_loop()
            elif self.state == "GAME":
                self.game_loop()
            elif self.state == "WIN":
                self.win_loop()
            else:
                break

    def menu_loop(self):
        # Main menu screen
        font_title = pygame.font.SysFont("Arial", 48)
        font_instr = pygame.font.SysFont("Arial", 32)
        title_text = font_title.render("Pinch Puzzle Deluxe", True, (255, 255, 255))
        instr_text = font_instr.render("Press ENTER to Start", True, (255, 255, 255))
        while self.state == "MENU":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.state = "GAME"
            self.screen.fill((0, 0, 0))
            self.screen.blit(title_text, ((self.width - title_text.get_width()) // 2, self.height // 3))
            self.screen.blit(instr_text, ((self.width - instr_text.get_width()) // 2, self.height // 2))
            pygame.display.flip()
            self.clock.tick(30)

    def game_loop(self):
        # Main game loop
        while self.state == "GAME":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()

            # Capture frame from the webcam
            ret, frame = self.cap.read()
            if not ret:
                continue
            frame = cv2.flip(frame, 1)
            results = self.get_hand_landmarks(frame)
            pinch_distance, finger_pos = None, (0, 0)
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    pinch_distance, finger_pos = self.get_pinch_status(handLms)
                    # (Optional) Draw hand landmarks on the frame for debugging:
                    mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            # Check pinch status based on a threshold (tweak as needed)
            if pinch_distance is not None and pinch_distance < 0.05:
                self.pinch_active = True
            else:
                self.pinch_active = False
                self.grabbed_piece = None  # release piece if pinch is not active

            # Handle dragging of puzzle pieces using pinch gesture
            if self.pinch_active:
                if self.grabbed_piece is None:
                    for piece in self.pieces:
                        if not piece.placed and piece.rect.collidepoint(finger_pos):
                            self.grabbed_piece = piece
                            break
                if self.grabbed_piece is not None:
                    # Move the piece to follow the finger (centering the piece)
                    self.grabbed_piece.rect.topleft = (finger_pos[0] - self.piece_width // 2,
                                                       finger_pos[1] - self.piece_height // 2)
            else:
                if self.grabbed_piece is not None:
                    # When the pinch is released, snap the piece into place if near its target
                    self.grabbed_piece.update()
                    self.grabbed_piece = None

            # Check if all pieces have been placed correctly
            if all(piece.placed for piece in self.pieces):
                self.state = "WIN"

            # -------------------- RENDERING --------------------
            # Draw the background
            if self.background:
                self.screen.blit(self.background, (0, 0))
            else:
                self.screen.fill((30, 30, 30))

            # Draw puzzle pieces
            for piece in self.pieces:
                piece.draw(self.screen)

            # Optionally, display a thumbnail of the camera feed in the corner
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(np.rot90(frame_rgb))
            thumb = pygame.transform.scale(frame_surface, (160, 120))
            self.screen.blit(thumb, (self.width - 170, 10))

            # Draw a visual indicator (a red circle) at the finger position when pinching
            if self.pinch_active:
                pygame.draw.circle(self.screen, (255, 0, 0), finger_pos, 10)

            pygame.display.flip()
            self.clock.tick(30)

    def win_loop(self):
        # Win screen when puzzle is complete
        font_win = pygame.font.SysFont("Arial", 48)
        font_instr = pygame.font.SysFont("Arial", 32)
        win_text = font_win.render("You Win!", True, (255, 255, 0))
        instr_text = font_instr.render("Press ENTER for Menu", True, (255, 255, 255))
        while self.state == "WIN":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Reset puzzle pieces for a new game
                        self.create_puzzle_pieces()
                        self.state = "MENU"
            self.screen.fill((0, 0, 0))
            self.screen.blit(win_text, ((self.width - win_text.get_width()) // 2, self.height // 3))
            self.screen.blit(instr_text, ((self.width - instr_text.get_width()) // 2, self.height // 2))
            pygame.display.flip()
            self.clock.tick(30)

    def cleanup(self):
        self.cap.release()
        pygame.quit()
        sys.exit()

# -------------------- ENTRY POINT --------------------
if __name__ == "__main__":
    game = PinchPuzzleDeluxe()
    game.run()
