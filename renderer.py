"""
OpenGL Renderer Module
Handles all OpenGL rendering using custom graphics algorithms
"""

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from typing import List, Tuple, Dict
from graphics_algorithms import CohenSutherland, SutherlandHodgman


class OpenGLRenderer:
    """
    OpenGL-based renderer that uses our custom rasterization algorithms
    """
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.pixel_buffer = {}  # Cache for pixels
        
        # Clipping window (viewport)
        self.clipper = CohenSutherland(0, 0, width, height)
        self.poly_clipper = SutherlandHodgman(0, 0, width, height)
    
    def init_gl(self):
        """Initialize OpenGL settings"""
        glClearColor(0.05, 0.05, 0.15, 1.0)  # Dark blue background
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Enable textures for text
        glEnable(GL_TEXTURE_2D)
        
        # Point size for pixel rendering
        glPointSize(1.0)
        
        # Font will be initialized when first needed
        self.font = None
        self.font_large = None
        
        # Simple bitmap font (5x7 pixel characters)
        self._init_bitmap_font()
    
    def _init_bitmap_font(self):
        """Initialize a simple 5x7 bitmap font using our algorithms"""
        # Define simple pixel patterns for characters (5 wide x 7 tall)
        # Each character is a list of (x, y) offsets from top-left
        self.char_width = 6
        self.char_height = 8
        
        self.bitmap_chars = {
            'A': [(0,6),(1,6),(2,5),(2,4),(2,3),(0,3),(1,3),(2,3),(0,2),(2,2),(0,1),(2,1),(0,0),(2,0)],
            'B': [(0,6),(1,6),(2,6),(0,5),(3,5),(0,4),(1,4),(2,4),(0,3),(3,3),(0,2),(3,2),(0,1),(3,1),(0,0),(1,0),(2,0)],
            'C': [(1,6),(2,6),(3,6),(0,5),(0,4),(0,3),(0,2),(0,1),(1,0),(2,0),(3,0)],
            'D': [(0,6),(1,6),(2,6),(0,5),(3,5),(0,4),(3,4),(0,3),(3,3),(0,2),(3,2),(0,1),(3,1),(0,0),(1,0),(2,0)],
            'E': [(0,6),(1,6),(2,6),(3,6),(0,5),(0,4),(0,3),(1,3),(2,3),(0,2),(0,1),(0,0),(1,0),(2,0),(3,0)],
            'F': [(0,6),(1,6),(2,6),(3,6),(0,5),(0,4),(0,3),(1,3),(2,3),(0,2),(0,1),(0,0)],
            'G': [(1,6),(2,6),(3,6),(0,5),(0,4),(0,3),(2,3),(3,3),(0,2),(3,2),(0,1),(3,1),(1,0),(2,0),(3,0)],
            'H': [(0,6),(3,6),(0,5),(3,5),(0,4),(3,4),(0,3),(1,3),(2,3),(3,3),(0,2),(3,2),(0,1),(3,1),(0,0),(3,0)],
            'I': [(1,6),(2,6),(3,6),(2,5),(2,4),(2,3),(2,2),(2,1),(1,0),(2,0),(3,0)],
            'J': [(3,6),(3,5),(3,4),(3,3),(3,2),(0,1),(3,1),(1,0),(2,0)],
            'K': [(0,6),(3,6),(0,5),(2,5),(0,4),(1,4),(0,3),(1,3),(0,2),(2,2),(0,1),(3,1),(0,0),(3,0)],
            'L': [(0,6),(0,5),(0,4),(0,3),(0,2),(0,1),(0,0),(1,0),(2,0),(3,0)],
            'M': [(0,6),(4,6),(0,5),(1,5),(3,5),(4,5),(0,4),(2,4),(4,4),(0,3),(4,3),(0,2),(4,2),(0,1),(4,1),(0,0),(4,0)],
            'N': [(0,6),(3,6),(0,5),(1,5),(3,5),(0,4),(2,4),(3,4),(0,3),(3,3),(0,2),(3,2),(0,1),(3,1),(0,0),(3,0)],
            'O': [(1,6),(2,6),(0,5),(3,5),(0,4),(3,4),(0,3),(3,3),(0,2),(3,2),(0,1),(3,1),(1,0),(2,0)],
            'P': [(0,6),(1,6),(2,6),(0,5),(3,5),(0,4),(3,4),(0,3),(1,3),(2,3),(0,2),(0,1),(0,0)],
            'Q': [(1,6),(2,6),(0,5),(3,5),(0,4),(3,4),(0,3),(3,3),(0,2),(2,2),(3,2),(0,1),(3,1),(1,0),(2,0),(4,0)],
            'R': [(0,6),(1,6),(2,6),(0,5),(3,5),(0,4),(3,4),(0,3),(1,3),(2,3),(0,2),(2,2),(0,1),(3,1),(0,0),(3,0)],
            'S': [(1,6),(2,6),(3,6),(0,5),(0,4),(1,3),(2,3),(3,2),(3,1),(0,0),(1,0),(2,0)],
            'T': [(0,6),(1,6),(2,6),(3,6),(4,6),(2,5),(2,4),(2,3),(2,2),(2,1),(2,0)],
            'U': [(0,6),(3,6),(0,5),(3,5),(0,4),(3,4),(0,3),(3,3),(0,2),(3,2),(0,1),(3,1),(1,0),(2,0)],
            'V': [(0,6),(4,6),(0,5),(4,5),(1,4),(3,4),(1,3),(3,3),(2,2),(2,1),(2,0)],
            'W': [(0,6),(4,6),(0,5),(4,5),(0,4),(2,4),(4,4),(0,3),(2,3),(4,3),(1,2),(3,2),(1,1),(3,1),(1,0),(3,0)],
            'X': [(0,6),(3,6),(0,5),(3,5),(1,4),(2,4),(1,3),(2,3),(1,2),(2,2),(0,1),(3,1),(0,0),(3,0)],
            'Y': [(0,6),(4,6),(1,5),(3,5),(2,4),(2,3),(2,2),(2,1),(2,0)],
            'Z': [(0,6),(1,6),(2,6),(3,6),(3,5),(2,4),(1,3),(0,2),(0,1),(0,0),(1,0),(2,0),(3,0)],
            '0': [(1,6),(2,6),(0,5),(3,5),(0,4),(2,4),(3,4),(0,3),(3,3),(0,2),(1,2),(3,2),(0,1),(3,1),(1,0),(2,0)],
            '1': [(1,6),(2,6),(2,5),(2,4),(2,3),(2,2),(2,1),(1,0),(2,0),(3,0)],
            '2': [(0,6),(1,6),(2,6),(3,5),(2,4),(1,3),(0,2),(0,1),(0,0),(1,0),(2,0),(3,0)],
            '3': [(0,6),(1,6),(2,6),(3,5),(3,4),(1,3),(2,3),(3,2),(3,1),(0,0),(1,0),(2,0)],
            '4': [(0,6),(3,6),(0,5),(3,5),(0,4),(3,4),(0,3),(1,3),(2,3),(3,3),(3,2),(3,1),(3,0)],
            '5': [(0,6),(1,6),(2,6),(3,6),(0,5),(0,4),(0,3),(1,3),(2,3),(3,2),(3,1),(0,0),(1,0),(2,0)],
            '6': [(1,6),(2,6),(0,5),(0,4),(0,3),(1,3),(2,3),(0,2),(3,2),(0,1),(3,1),(1,0),(2,0)],
            '7': [(0,6),(1,6),(2,6),(3,6),(3,5),(2,4),(2,3),(1,2),(1,1),(1,0)],
            '8': [(1,6),(2,6),(0,5),(3,5),(0,4),(3,4),(1,3),(2,3),(0,2),(3,2),(0,1),(3,1),(1,0),(2,0)],
            '9': [(1,6),(2,6),(0,5),(3,5),(0,4),(3,4),(1,3),(2,3),(3,3),(3,2),(3,1),(1,0),(2,0)],
            ' ': [],
            ':': [(2,5),(2,4),(2,1),(2,0)],
            '-': [(1,3),(2,3),(3,3)],
            '!': [(2,6),(2,5),(2,4),(2,3),(2,2),(2,0)],
            '.': [(2,0)],
            '/': [(3,6),(3,5),(2,4),(2,3),(1,2),(1,1),(0,0)],
            'm': [(0,4),(1,4),(3,4),(0,3),(2,3),(4,3),(0,2),(2,2),(4,2),(0,1),(2,1),(4,1),(0,0),(2,0),(4,0)],
        }
    
    def _init_fonts(self):
        """Initialize fonts on first use - now using bitmap fonts"""
        pass  # Using bitmap font instead
    
    def clear(self):
        """Clear the screen"""
        glClear(GL_COLOR_BUFFER_BIT)
    
    def draw_pixel(self, x: int, y: int, color: Tuple[float, float, float], alpha: float = 1.0):
        """Draw a single pixel"""
        if 0 <= x < self.width and 0 <= y < self.height:
            glColor4f(color[0], color[1], color[2], alpha)
            glBegin(GL_POINTS)
            glVertex2f(x + 0.5, y + 0.5)
            glEnd()
    
    def draw_pixels(self, pixels: List[Tuple[int, int]], color: Tuple[float, float, float], alpha: float = 1.0):
        """Draw multiple pixels efficiently"""
        if not pixels:
            return
        
        glColor4f(color[0], color[1], color[2], alpha)
        glBegin(GL_POINTS)
        for x, y in pixels:
            if 0 <= x < self.width and 0 <= y < self.height:
                glVertex2f(x + 0.5, y + 0.5)
        glEnd()
    
    def draw_pixels_large(self, pixels: List[Tuple[int, int]], color: Tuple[float, float, float], 
                          alpha: float = 1.0, size: int = 2):
        """Draw pixels as small quads for better visibility"""
        if not pixels:
            return
        
        glColor4f(color[0], color[1], color[2], alpha)
        half = size / 2
        
        glBegin(GL_QUADS)
        for x, y in pixels:
            if 0 <= x < self.width and 0 <= y < self.height:
                glVertex2f(x - half, y - half)
                glVertex2f(x + half, y - half)
                glVertex2f(x + half, y + half)
                glVertex2f(x - half, y + half)
        glEnd()
    
    def draw_line_bresenham(self, x1: int, y1: int, x2: int, y2: int, 
                            color: Tuple[float, float, float], alpha: float = 1.0):
        """Draw a line using Bresenham's algorithm with clipping"""
        # Apply Cohen-Sutherland clipping
        accepted, (cx1, cy1, cx2, cy2) = self.clipper.clip_line(x1, y1, x2, y2)
        
        if not accepted:
            return
        
        from graphics_algorithms import bresenham_line
        pixels = bresenham_line(int(cx1), int(cy1), int(cx2), int(cy2))
        self.draw_pixels(pixels, color, alpha)
    
    def draw_circle_midpoint(self, xc: int, yc: int, r: int, 
                             color: Tuple[float, float, float], filled: bool = False, alpha: float = 1.0):
        """Draw a circle using midpoint algorithm"""
        from graphics_algorithms import midpoint_circle, filled_circle
        
        if filled:
            pixels = filled_circle(xc, yc, r)
        else:
            pixels = midpoint_circle(xc, yc, r)
        
        self.draw_pixels(pixels, color, alpha)
    
    def draw_ellipse_midpoint(self, xc: int, yc: int, rx: int, ry: int,
                              color: Tuple[float, float, float], filled: bool = False, alpha: float = 1.0):
        """Draw an ellipse using midpoint algorithm"""
        from graphics_algorithms import midpoint_ellipse, filled_ellipse
        
        if filled:
            pixels = filled_ellipse(xc, yc, rx, ry)
        else:
            pixels = midpoint_ellipse(xc, yc, rx, ry)
        
        self.draw_pixels(pixels, color, alpha)
    
    def draw_polygon(self, vertices: List[Tuple[float, float]], 
                     color: Tuple[float, float, float], filled: bool = False, 
                     alpha: float = 1.0, clip: bool = True):
        """Draw a polygon using Bresenham's lines, with optional clipping"""
        if not vertices:
            return
        
        # Apply Sutherland-Hodgman clipping if enabled
        if clip:
            vertices = self.poly_clipper.clip_polygon(vertices)
            if not vertices:
                return
        
        from graphics_algorithms import filled_polygon, polygon_from_lines
        
        if filled:
            pixels = filled_polygon(vertices)
        else:
            pixels = polygon_from_lines(vertices)
        
        self.draw_pixels(pixels, color, alpha)
    
    def draw_rectangle(self, x: float, y: float, width: float, height: float,
                       color: Tuple[float, float, float], filled: bool = True, alpha: float = 1.0):
        """Draw a rectangle"""
        vertices = [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height)
        ]
        self.draw_polygon(vertices, color, filled, alpha)
    
    def draw_gradient_background(self, top_color: Tuple[float, float, float],
                                  bottom_color: Tuple[float, float, float]):
        """Draw a vertical gradient background"""
        glBegin(GL_QUADS)
        glColor3f(*bottom_color)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glColor3f(*top_color)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()
    
    def draw_text_bitmap(self, x: int, y: int, text: str, 
                         color: Tuple[float, float, float] = (1, 1, 1), large: bool = False):
        """Draw text using our custom bitmap font with Bresenham-based pixels"""
        scale = 2 if large else 1
        cursor_x = x
        
        for char in text.upper():
            if char in self.bitmap_chars:
                pixels = []
                for px, py in self.bitmap_chars[char]:
                    for sx in range(scale):
                        for sy in range(scale):
                            pixels.append((cursor_x + px * scale + sx, y + py * scale + sy))
                self.draw_pixels(pixels, color)
            cursor_x += self.char_width * scale
    
    # ========================================================================
    # HIGH-LEVEL DRAWING FUNCTIONS FOR GAME OBJECTS
    # ========================================================================
    
    def draw_airplane(self, airplane):
        """Draw the airplane using rasterization algorithms"""
        render_data = airplane.get_render_data()
        
        # Draw body (filled)
        self.draw_pixels_large(render_data['body'], airplane.body_color, size=2)
        
        # Draw body outline
        self.draw_pixels(render_data['body_outline'], (0.2, 0.2, 0.2))
        
        # Draw wings
        self.draw_pixels_large(render_data['wings'], (0.7, 0.7, 0.8), size=2)
        
        # Draw tail
        self.draw_pixels_large(render_data['tail'], (0.6, 0.6, 0.7), size=2)
        
        # Draw cockpit (glass - blue tint)
        self.draw_pixels_large(render_data['cockpit'], (0.3, 0.5, 0.8), size=2)
        
        # Draw engine
        self.draw_pixels_large(render_data['engine'], (0.4, 0.4, 0.4), size=2)
        
        # Draw propeller
        self.draw_pixels(render_data['propeller'], (0.3, 0.3, 0.3))
        
        # Boost flame effect
        if airplane.is_boosting:
            # Draw engine flame
            import random
            flame_x = int(airplane.x - 35)
            flame_y = int(airplane.y)
            flame_colors = [(1, 0.8, 0), (1, 0.5, 0), (1, 0.2, 0)]
            for i, color in enumerate(flame_colors):
                length = random.randint(10, 25) - i * 5
                from graphics_algorithms import filled_ellipse
                pixels = filled_ellipse(flame_x - i * 8, flame_y, length, 4 - i)
                self.draw_pixels(pixels, color, 0.8)
    
    def draw_missile(self, missile):
        """Draw a missile using rasterization algorithms"""
        render_data = missile.get_render_data()
        
        # Draw body
        self.draw_pixels_large(render_data['body'], missile.body_color, size=2)
        
        # Draw nose (red)
        self.draw_pixels_large(render_data['nose'], missile.color, size=2)
        
        # Draw flame
        flame_colors = [(1, 0.8, 0), (1, 0.5, 0), (1, 0.2, 0)]
        import random
        self.draw_pixels(render_data['flame'], flame_colors[random.randint(0, 2)], 0.9)
        
        # Draw outline
        self.draw_pixels(render_data['outline'], (0.2, 0.2, 0.2))
    
    def draw_cloud(self, cloud):
        """Draw a cloud using midpoint circles"""
        render_data = cloud.get_render_data()
        self.draw_pixels_large(render_data['circles'], cloud.color, cloud.alpha, size=2)
    
    def draw_fuel(self, fuel):
        """Draw a fuel canister"""
        render_data = fuel.get_render_data()
        
        # Draw body (green)
        self.draw_pixels_large(render_data['body'], fuel.color, size=2)
        
        # Draw cap
        self.draw_pixels_large(render_data['cap'], (0.5, 0.5, 0.5), size=2)
        
        # Draw plus symbol (white)
        self.draw_pixels(render_data['symbol'], (1, 1, 1))
    
    def draw_star(self, star):
        """Draw a background star"""
        render_data = star.get_render_data()
        brightness = render_data['brightness']
        color = (brightness, brightness, brightness * 0.9)
        self.draw_pixels(render_data['points'], color)
    
    def draw_explosion(self, explosion):
        """Draw an explosion effect"""
        render_data = explosion.get_render_data()
        
        for particle in render_data['particles']:
            self.draw_pixels(particle['points'], particle['color'], particle['alpha'])
    
    def draw_ground(self, ground):
        """Draw the scrolling ground"""
        render_data = ground.get_render_data()
        
        # Draw ground fill (brown)
        self.draw_pixels_large(render_data['ground'], (0.4, 0.25, 0.1), size=2)
        
        # Draw grass line (green)
        self.draw_pixels(render_data['grass'], (0.2, 0.6, 0.2))
    
    # ========================================================================
    # UI DRAWING FUNCTIONS
    # ========================================================================
    
    def draw_fuel_bar(self, fuel: float, max_fuel: float, x: int, y: int, width: int, height: int):
        """Draw a fuel gauge"""
        # Background
        self.draw_rectangle(x, y, width, height, (0.2, 0.2, 0.2))
        
        # Fuel level
        fuel_width = int((fuel / max_fuel) * (width - 4))
        if fuel_width > 0:
            # Color based on fuel level
            ratio = fuel / max_fuel
            if ratio > 0.5:
                color = (0.2, 0.8, 0.2)  # Green
            elif ratio > 0.25:
                color = (0.8, 0.8, 0.2)  # Yellow
            else:
                color = (0.8, 0.2, 0.2)  # Red
            
            self.draw_rectangle(x + 2, y + 2, fuel_width, height - 4, color)
        
        # Border using Bresenham lines
        self.draw_line_bresenham(x, y, x + width, y, (1, 1, 1))
        self.draw_line_bresenham(x, y + height, x + width, y + height, (1, 1, 1))
        self.draw_line_bresenham(x, y, x, y + height, (1, 1, 1))
        self.draw_line_bresenham(x + width, y, x + width, y + height, (1, 1, 1))
    
    def draw_score(self, distance: int, missiles_dodged: int, x: int, y: int):
        """Draw the score display"""
        # Background panel
        self.draw_rectangle(x, y, 150, 50, (0, 0, 0), alpha=0.5)
        
        # Draw score text (using simple pixel text would be complex, use GLUT)
        self.draw_text_bitmap(x + 10, y + 30, f"Distance: {distance}m", (1, 1, 1))
        self.draw_text_bitmap(x + 10, y + 10, f"Dodged: {missiles_dodged}", (1, 1, 0))
    
    def draw_game_over(self, distance: int, missiles_dodged: int):
        """Draw game over screen"""
        # Darken background
        glColor4f(0, 0, 0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height)
        glVertex2f(0, self.height)
        glEnd()
        
        # Game over panel
        panel_width = 400
        panel_height = 200
        px = (self.width - panel_width) // 2
        py = (self.height - panel_height) // 2
        
        self.draw_rectangle(px, py, panel_width, panel_height, (0.1, 0.1, 0.2), alpha=0.9)
        
        # Border
        self.draw_line_bresenham(px, py, px + panel_width, py, (1, 0.3, 0.3))
        self.draw_line_bresenham(px, py + panel_height, px + panel_width, py + panel_height, (1, 0.3, 0.3))
        self.draw_line_bresenham(px, py, px, py + panel_height, (1, 0.3, 0.3))
        self.draw_line_bresenham(px + panel_width, py, px + panel_width, py + panel_height, (1, 0.3, 0.3))
        
        # Text
        self.draw_text_bitmap(px + 130, py + 160, "GAME OVER", (1, 0.3, 0.3))
        self.draw_text_bitmap(px + 100, py + 120, f"Distance: {distance} meters", (1, 1, 1))
        self.draw_text_bitmap(px + 100, py + 90, f"Missiles Dodged: {missiles_dodged}", (1, 1, 0))
        self.draw_text_bitmap(px + 100, py + 40, "Press SPACE to restart", (0.7, 0.7, 0.7))
        self.draw_text_bitmap(px + 100, py + 20, "Press ESC to quit", (0.7, 0.7, 0.7))
    
    def draw_start_screen(self):
        """Draw the start/title screen"""
        # Background gradient
        self.draw_gradient_background((0.1, 0.1, 0.3), (0.0, 0.0, 0.1))
        
        # Title
        self.draw_text_bitmap(self.width // 2 - 100, self.height - 150, 
                             "AIRPLANE GAME", (1, 1, 1))
        
        # Subtitle
        self.draw_text_bitmap(self.width // 2 - 150, self.height - 200,
                             "Computer Graphics Mini Project", (0.7, 0.7, 0.9))
        
        # Instructions
        instructions = [
            "Controls:",
            "UP / W - Fly Up",
            "DOWN / S - Fly Down", 
            "SPACE - Boost (uses fuel)",
            "",
            "Avoid missiles and collect fuel!",
            "",
            "Press SPACE to Start",
            "Press ESC to Quit"
        ]
        
        y = self.height // 2 + 50
        for line in instructions:
            self.draw_text_bitmap(self.width // 2 - 100, y, line, (0.8, 0.8, 0.8))
            y -= 25
        
        # Draw decorative airplane
        from graphics_algorithms import bresenham_line, filled_ellipse
        
        # Simple airplane silhouette
        ax, ay = self.width // 2, self.height - 100
        # Fuselage
        pixels = filled_ellipse(ax, ay, 40, 10)
        self.draw_pixels(pixels, (0.3, 0.6, 1.0))
        # Wings
        wing_pixels = filled_ellipse(ax - 10, ay, 10, 25)
        self.draw_pixels(wing_pixels, (0.4, 0.7, 1.0))
    
    def draw_hud(self, airplane, distance: int, missiles_dodged: int):
        """Draw the heads-up display"""
        # Fuel bar
        self.draw_fuel_bar(airplane.fuel, airplane.max_fuel, 20, self.height - 40, 200, 20)
        self.draw_text_bitmap(25, self.height - 35, "FUEL", (1, 1, 1))
        
        # Score
        self.draw_text_bitmap(self.width - 200, self.height - 30, 
                             f"Distance: {distance}m", (1, 1, 1))
        self.draw_text_bitmap(self.width - 200, self.height - 55,
                             f"Dodged: {missiles_dodged}", (1, 1, 0))
        
        # Boost indicator
        if airplane.is_boosting:
            self.draw_text_bitmap(20, self.height - 70, "BOOST!", (1, 0.5, 0))
