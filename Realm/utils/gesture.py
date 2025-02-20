# utils/gesture.py
import cv2
import mediapipe as mp
import numpy as np
from config import SCREEN_WIDTH, SCREEN_HEIGHT

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def get_hand_landmarks(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    return results

def get_pinch_status(landmarks):
    # Get the thumb tip and index finger tip.
    thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    # Calculate Euclidean distance.
    x1, y1 = thumb_tip.x, thumb_tip.y
    x2, y2 = index_tip.x, index_tip.y
    dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    # Convert normalized index tip to screen coordinates.
    finger_pos = (int(index_tip.x * SCREEN_WIDTH), int(index_tip.y * SCREEN_HEIGHT))
    return dist, finger_pos
