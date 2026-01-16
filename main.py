"""
Airplane Game - Main Entry Point
A 2D Interactive Graphics Simulation

Computer Graphics Mini Project
Demonstrates: Bresenham's Line, Midpoint Circle/Ellipse, 
              2D Transformations, Cohen-Sutherland & Sutherland-Hodgman Clipping

Controls:
    UP/W    - Fly up
    DOWN/S  - Fly down
    SPACE   - Boost (consumes extra fuel)
    ESC     - Quit

Author: Computer Graphics Project
"""

import sys
import random
import time

# Pygame for window management and input
import pygame
from pygame.locals import *

# OpenGL for rendering
from OpenGL.GL import *
from OpenGL.GLU import *

# Game modules
from game_objects import (
    Airplane, Missile, Cloud, FuelCanister, 
    Star, Explosion, Ground
)
from renderer import OpenGLRenderer
from graphics_algorithms import Transform2D


class GameState:
    """Enum-like class for game states"""
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3


class AirplaneGame:
    """
    Main game class
    Manages game loop, objects, and state
    """
    
    def __init__(self, width: int = 1024, height: int = 600):
        self.width = width
        self.height = height
        self.running = True
        self.state = GameState.MENU
        
        # Initialize Pygame
        pygame.init()
        pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Airplane Game - Computer Graphics Project")
        
        # Initialize renderer
        self.renderer = OpenGLRenderer(width, height)
        self.renderer.init_gl()
        
        # Game clock
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        
        # Input state
        self.keys = {
            'up': False,
            'down': False,
            'boost': False
        }
        
        # Game statistics
        self.distance = 0
        self.missiles_dodged = 0
        self.scroll_speed = 100  # pixels per second
        
        # Initialize game objects
        self.init_game_objects()
    
    def init_game_objects(self):
        """Initialize or reset all game objects"""
        # Player airplane
        self.airplane = Airplane(150, self.height // 2)
        
        # Missiles (enemies)
        self.missiles = []
        self.missile_spawn_timer = 0
        self.missile_spawn_interval = 2.0  # seconds
        
        # Clouds (decoration)
        self.clouds = []
        for _ in range(5):
            x = random.randint(0, self.width)
            y = random.randint(self.height // 2, self.height - 50)
            self.clouds.append(Cloud(x, y))
        
        # Fuel canisters
        self.fuel_canisters = []
        self.fuel_spawn_timer = 0
        self.fuel_spawn_interval = 8.0  # seconds
        
        # Stars (background parallax)
        self.stars = []
        for layer in range(3):
            for _ in range(20):
                x = random.randint(0, self.width)
                y = random.randint(100, self.height - 50)
                self.stars.append(Star(x, y, layer))
        
        # Explosions
        self.explosions = []
        
        # Ground
        self.ground = Ground(self.width, 50)
        
        # Reset stats
        self.distance = 0
        self.missiles_dodged = 0
        self.scroll_speed = 100
    
    def handle_events(self):
        """Process input events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    else:
                        self.running = False
                
                elif event.key == K_SPACE:
                    if self.state == GameState.MENU:
                        self.state = GameState.PLAYING
                        self.init_game_objects()
                    elif self.state == GameState.GAME_OVER:
                        self.state = GameState.PLAYING
                        self.init_game_objects()
                    elif self.state == GameState.PLAYING:
                        self.keys['boost'] = True
                
                elif event.key in (K_UP, K_w):
                    self.keys['up'] = True
                elif event.key in (K_DOWN, K_s):
                    self.keys['down'] = True
                
                elif event.key == K_p:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
            
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    self.keys['boost'] = False
                elif event.key in (K_UP, K_w):
                    self.keys['up'] = False
                elif event.key in (K_DOWN, K_s):
                    self.keys['down'] = False
    
    def spawn_missile(self):
        """Spawn a new missile from the right side"""
        y = random.randint(80, self.height - 80)
        missile = Missile(self.width + 50, y)
        self.missiles.append(missile)
    
    def spawn_fuel(self):
        """Spawn a fuel canister"""
        y = random.randint(100, self.height - 100)
        fuel = FuelCanister(self.width + 30, y)
        self.fuel_canisters.append(fuel)
    
    def spawn_cloud(self):
        """Spawn a new cloud"""
        y = random.randint(self.height // 2, self.height - 50)
        cloud = Cloud(self.width + 50, y)
        self.clouds.append(cloud)
    
    def update(self, dt: float):
        """Update game state"""
        if self.state != GameState.PLAYING:
            return
        
        # Update airplane
        self.airplane.update(dt, self.keys)
        
        # Check for game over (out of fuel)
        if self.airplane.fuel <= 0:
            self.explosions.append(Explosion(self.airplane.x, self.airplane.y))
            self.state = GameState.GAME_OVER
            return
        
        # Update distance
        effective_speed = self.scroll_speed
        if self.airplane.is_boosting:
            effective_speed *= 1.5
        self.distance += int(effective_speed * dt)
        
        # Increase difficulty over time
        self.scroll_speed = 100 + self.distance // 500
        self.missile_spawn_interval = max(0.5, 2.0 - self.distance / 5000)
        
        # Spawn missiles
        self.missile_spawn_timer += dt
        if self.missile_spawn_timer >= self.missile_spawn_interval:
            self.spawn_missile()
            self.missile_spawn_timer = 0
            
            # Occasionally spawn extra missiles
            if random.random() < 0.3:
                self.spawn_missile()
        
        # Spawn fuel
        self.fuel_spawn_timer += dt
        if self.fuel_spawn_timer >= self.fuel_spawn_interval:
            self.spawn_fuel()
            self.fuel_spawn_timer = 0
        
        # Update missiles
        for missile in self.missiles[:]:
            missile.update(dt)
            
            # Check collision with airplane
            if missile.collides_with(self.airplane):
                self.explosions.append(Explosion(self.airplane.x, self.airplane.y))
                self.state = GameState.GAME_OVER
                return
            
            # Remove if off screen
            if missile.x < -100:
                self.missiles.remove(missile)
                self.missiles_dodged += 1
        
        # Update fuel canisters
        for fuel in self.fuel_canisters[:]:
            fuel.update(dt)
            
            # Check collection
            if fuel.collides_with(self.airplane):
                self.airplane.fuel = min(self.airplane.max_fuel, 
                                        self.airplane.fuel + fuel.fuel_amount)
                self.fuel_canisters.remove(fuel)
            elif fuel.x < -50:
                self.fuel_canisters.remove(fuel)
        
        # Update clouds
        for cloud in self.clouds[:]:
            cloud.update(dt)
            if cloud.x < -100:
                self.clouds.remove(cloud)
        
        # Spawn new clouds occasionally
        if random.random() < 0.02:
            self.spawn_cloud()
        
        # Update stars (parallax)
        for star in self.stars:
            star.update(dt)
            if star.x < 0:
                star.x = self.width
                star.y = random.randint(100, self.height - 50)
        
        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update(dt)
            if not explosion.active:
                self.explosions.remove(explosion)
        
        # Update ground
        self.ground.update(dt, effective_speed)
    
    def render(self):
        """Render the game"""
        self.renderer.clear()
        
        if self.state == GameState.MENU:
            self.renderer.draw_start_screen()
        
        elif self.state in (GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER):
            # Background gradient (sky)
            self.renderer.draw_gradient_background(
                (0.4, 0.6, 0.9),  # Light blue (top)
                (0.7, 0.8, 1.0)   # Lighter blue (horizon)
            )
            
            # Draw stars (far background)
            for star in self.stars:
                self.renderer.draw_star(star)
            
            # Draw clouds
            for cloud in self.clouds:
                self.renderer.draw_cloud(cloud)
            
            # Draw ground
            self.renderer.draw_ground(self.ground)
            
            # Draw fuel canisters
            for fuel in self.fuel_canisters:
                self.renderer.draw_fuel(fuel)
            
            # Draw missiles
            for missile in self.missiles:
                self.renderer.draw_missile(missile)
            
            # Draw airplane
            if self.state != GameState.GAME_OVER:
                self.renderer.draw_airplane(self.airplane)
            
            # Draw explosions
            for explosion in self.explosions:
                self.renderer.draw_explosion(explosion)
            
            # Draw HUD
            self.renderer.draw_hud(self.airplane, self.distance, self.missiles_dodged)
            
            # Draw pause overlay
            if self.state == GameState.PAUSED:
                self.draw_pause_overlay()
            
            # Draw game over screen
            elif self.state == GameState.GAME_OVER:
                self.renderer.draw_game_over(self.distance, self.missiles_dodged)
        
        # Swap buffers
        pygame.display.flip()
    
    def draw_pause_overlay(self):
        """Draw pause screen overlay"""
        # Semi-transparent overlay
        glColor4f(0, 0, 0, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()
        
        # Pause text
        self.renderer.draw_text_bitmap(
            self.width // 2 - 40, self.height // 2,
            "PAUSED", (1, 1, 1)
        )
        self.renderer.draw_text_bitmap(
            self.width // 2 - 80, self.height // 2 - 30,
            "Press P or ESC to continue", (0.7, 0.7, 0.7)
        )
    
    def run(self):
        """Main game loop"""
        last_time = time.time()
        
        while self.running:
            # Calculate delta time
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Cap delta time to prevent huge jumps
            dt = min(dt, 0.1)
            
            # Handle input
            self.handle_events()
            
            # Update game state
            self.update(dt)
            
            # Render
            self.render()
            
            # Cap frame rate
            self.clock.tick(self.target_fps)
        
        pygame.quit()


def main():
    """Entry point"""
    print("=" * 60)
    print("AIRPLANE GAME - Computer Graphics Mini Project")
    print("=" * 60)
    print()
    print("This game demonstrates:")
    print("  - Bresenham's Line Drawing Algorithm")
    print("  - Midpoint Circle Algorithm")
    print("  - Midpoint Ellipse Algorithm")
    print("  - 2D Transformations (Homogeneous Matrices)")
    print("  - Cohen-Sutherland Line Clipping")
    print("  - Sutherland-Hodgman Polygon Clipping")
    print()
    print("Controls:")
    print("  UP/W    - Fly up")
    print("  DOWN/S  - Fly down")
    print("  SPACE   - Boost (uses fuel)")
    print("  P       - Pause")
    print("  ESC     - Quit/Back")
    print()
    print("Starting game...")
    print()
    
    game = AirplaneGame()
    game.run()


if __name__ == "__main__":
    main()
