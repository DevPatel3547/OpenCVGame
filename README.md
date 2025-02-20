# Gesture-Controlled Games Collection

This repository is a comprehensive showcase of innovative, gesture-controlled games developed in Python using Pygame, OpenCV, and Mediapipe. The collection demonstrates a progression from simple prototypes to large-scale, multi-module projects—all leveraging hand-tracking and gesture recognition for immersive gameplay.

## Overview

This collection includes three distinct projects:

- **Pinch Puzzle Game** – A simple puzzle game where players use pinch gestures detected by their webcam to drag and drop puzzle pieces.
- **Space Gesture Shooter** – A fast-paced, arcade-style shooter where a spaceship is controlled by finger movements, and a pinch gesture fires lasers at incoming enemy ships.
- **Realm of Gestures: Odyssey** – A full-fledged, gesture-controlled 2D action-adventure RPG with a vast, tile-based world, scrolling camera, dynamic enemy AI, and modular multi-file architecture.

Each project is designed to highlight various aspects of gesture control, game design, and advanced programming techniques—from basic interactive puzzles to expansive worlds with sophisticated game mechanics.

## Features

### Pinch Puzzle Game
- Utilizes the webcam to detect hand landmarks and pinch gestures using Mediapipe and OpenCV.
- Implements a drag-and-drop mechanic to assemble puzzle pieces into a complete image.
- Simple yet effective demonstration of computer vision integration with game mechanics.

### Space Gesture Shooter
- Real-time gesture recognition to steer a spaceship and trigger attacks.
- Dynamic enemy spawning and projectile combat in a space-themed environment.
- Incorporates visual feedback such as a live camera thumbnail and on-screen indicators for pinch gestures.

### Realm of Gestures: Odyssey
- A fully modular 2D action-adventure RPG with a procedurally generated, tile-based world.
- Features a scrolling camera system that centers on the player within a massive world.
- Enemy AI, projectile combat, and comprehensive HUD elements (score and health).
- Organized across multiple modules and directories for improved scalability and maintainability.

## Project Structure

The repository is organized into separate directories for each game, along with shared assets and utility functions. A typical project structure includes:

- A main entry point file for launching the game.
- A configuration module that holds constants (screen dimensions, asset paths, etc.).
- An `assets/` folder containing fonts, images, and sound files for visual and audio enhancements.
- `engine/` directories containing modules for game logic, camera handling, world generation, player and enemy classes, and projectile management.
- `utility/` directories for gesture recognition functions and miscellaneous helper routines.

Each project is self-contained, yet they share similar design philosophies—making use of modular code, clear state management (menus, gameplay, and game-over screens), and robust gesture input handling.

## Requirements

To run any of the games in this collection, you will need:

- Python 3.8 or higher
- Pygame
- OpenCV-Python
- Mediapipe
- Numpy

Ensure your Python environment is properly configured with these libraries before launching a game.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/DevPatel3547/OpenCVGame.git
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Ensure that all assets (such as images, fonts, and sounds) are placed in the appropriate folders as outlined in the project structure.

## Running the Games

Each game in the collection is launched via its main entry point file. When executed, a game window will open displaying an initial menu screen with instructions. Use your hand gestures—as captured by your webcam—to control the game:

- **Pinch Puzzle Game**: Use pinch gestures to select and move puzzle pieces.
- **Space Gesture Shooter**: Your finger position controls the spaceship while a pinch gesture fires projectiles at enemies.
- **Realm of Gestures: Odyssey**: Your hand movements navigate the player through a vast world, and a pinch gesture initiates attacks against approaching foes.

- ### **To run the games, cd into the particular game directory and run the following commands**:
- **Pinch Puzzle Game**: ```python3 pinch_puzzle.py```
- **Space Gesture Shooter**: ```python3 space_gesture_shooter.py```
- **Realm of Gestures: Odyssey**: ```python3 main.py```

Follow the on-screen instructions to begin gameplay, and refer to the HUD for real-time updates on your score, health, and game status.

## Controls and Mechanics

### Gesture-Based Interaction
- The games use Mediapipe to process webcam input and extract hand landmarks.
- A pinch gesture (bringing the thumb and index finger close together) is interpreted as a command (e.g., to drag a puzzle piece or fire a projectile).

### Movement
- In all games, the player's position is dynamically updated to follow the detected finger position.
- In larger projects like *Realm of Gestures: Odyssey*, movement is smoothed out and mapped into a scrolling, tile-based world.

### Combat and Interactions
- Actions such as dragging, attacking, and interacting with enemies are triggered via specific gestures.
- Real-time collision detection, enemy AI, and projectile physics provide engaging and responsive gameplay experiences.

### HUD and Feedback
- Each game features a heads-up display that communicates essential information such as score, health, and active gestures.
- Visual indicators (such as live camera thumbnails and gesture markers) offer immediate feedback on user interactions.

## Extensibility and Future Improvements

The design of these projects is highly modular and scalable. Future enhancements may include:

- Integrating high-resolution art assets and custom animations.
- Adding particle effects and advanced visual feedback for improved immersion.
- Expanding enemy types and AI behaviors in combat scenarios.
- Incorporating sound effects and background music using Pygame’s audio mixer.
- Further modularizing code for better maintainability and cross-platform support.
- Implementing multiplayer features and networked gameplay.

Contributions to expand functionality or improve overall game quality are welcome. Please follow standard GitHub contribution workflows if you wish to contribute.

## Contribution and License

Contributions to the **Gesture-Controlled Games Collection** are welcome. Please fork the repository and submit pull requests following best practices. This project is provided for educational and prototyping purposes; 

## Acknowledgments

Special thanks to the communities behind **Pygame**, **OpenCV**, and **Mediapipe**. Their tools and resources have been instrumental in the development of these innovative gesture-controlled games.
