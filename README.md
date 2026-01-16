# Airplane Game - Computer Graphics Mini Project
# Python 3 + OpenGL Implementation

## Requirements
- Python 3.9+
- PyOpenGL
- pygame
- numpy

## Installation

### macOS (Apple Silicon M3)

```bash
# Install Python dependencies
pip3 install pygame PyOpenGL PyOpenGL_accelerate numpy

# If PyOpenGL_accelerate fails, just use:
pip3 install pygame PyOpenGL numpy
```

## Running the Game

```bash
cd /Users/adi/adi/Computer_Graphics_Mini_Project/PythonGame
python3 main.py
```

## Controls
- **UP / W** - Fly up
- **DOWN / S** - Fly down
- **SPACE** - Boost (uses extra fuel)
- **P** - Pause
- **ESC** - Quit

## Project Structure

```
PythonGame/
├── main.py                 # Main game entry point and game loop
├── game_objects.py         # Game entities (Airplane, Missile, Cloud, etc.)
├── renderer.py             # OpenGL rendering using custom algorithms
├── graphics_algorithms.py  # Core CG algorithms implementation
└── README.md              # This file
```

## Implemented Computer Graphics Algorithms

### 1. Bresenham's Line Drawing Algorithm
- Used for drawing polygon outlines
- Used for propeller blades
- Used for UI elements
- Efficient integer-only arithmetic

### 2. Midpoint Circle Algorithm
- Used for drawing circular objects (clouds, engine)
- Both outline and filled versions
- Uses 8-way symmetry for efficiency

### 3. Midpoint Ellipse Algorithm  
- Used for airplane cockpit
- Used for engine flames
- Both outline and filled versions
- Uses 4-way symmetry

### 4. 2D Transformations (Homogeneous Coordinates)
All transformations use 3x3 homogeneous matrices with homogeneity factor = 1:

- **Translation**: Moving objects in x/y directions
- **Rotation**: Airplane tilt based on movement
- **Scaling**: Object size adjustments
- **Composite Transformations**: Rotation about arbitrary points

Matrix form:
```
| a  b  tx |   | x |   | x' |
| c  d  ty | × | y | = | y' |
| 0  0  1  |   | 1 |   | 1  |
```

### 5. Cohen-Sutherland Line Clipping
- Clips lines against viewport boundaries
- Uses 4-bit region codes
- Trivial accept/reject optimization

### 6. Sutherland-Hodgman Polygon Clipping
- Clips polygons against rectangular viewport
- Sequential edge clipping approach
- Handles complex polygon shapes

## Game Features

- Scrolling background with parallax layers
- Dynamic missile spawning with increasing difficulty
- Fuel system and collectible fuel canisters
- Collision detection using AABB
- Particle-based explosion effects
- Animated propeller using rotation transformation
- Ground terrain with scrolling

## Authors
Computer Graphics Mini Project Team
