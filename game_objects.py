"""
Game Objects Module
Defines the Airplane, Missiles, Clouds, and other game elements
Uses custom graphics algorithms for rendering
"""

import random
import math
from typing import List, Tuple
from graphics_algorithms import (
    bresenham_line, midpoint_circle, midpoint_ellipse,
    filled_circle, filled_ellipse, filled_polygon,
    Transform2D, CohenSutherland, SutherlandHodgman
)
import numpy as np


class GameObject:
    """Base class for all game objects"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.rotation = 0  # degrees
        self.scale = 1.0
        self.active = True
        self.color = (1.0, 1.0, 1.0)  # RGB
    
    def update(self, dt: float):
        """Update object position"""
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
    
    def get_transform_matrix(self) -> np.ndarray:
        """Get the combined transformation matrix"""
        T = Transform2D.translation_matrix(self.x, self.y)
        R = Transform2D.rotation_matrix(self.rotation)
        S = Transform2D.scaling_matrix(self.scale, self.scale)
        return T @ R @ S
    
    def get_vertices(self) -> List[Tuple[float, float]]:
        """Override in subclasses to return object vertices"""
        return []
    
    def get_transformed_vertices(self) -> List[Tuple[float, float]]:
        """Get vertices after applying transformations"""
        matrix = self.get_transform_matrix()
        return Transform2D.transform_points(self.get_vertices(), matrix)
    
    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        """Returns (min_x, min_y, max_x, max_y)"""
        vertices = self.get_transformed_vertices()
        if not vertices:
            return (self.x - 10, self.y - 10, self.x + 10, self.y + 10)
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        return (min(xs), min(ys), max(xs), max(ys))
    
    def collides_with(self, other: 'GameObject') -> bool:
        """Simple AABB collision detection"""
        box1 = self.get_bounding_box()
        box2 = other.get_bounding_box()
        
        return not (box1[2] < box2[0] or  # self.max_x < other.min_x
                   box1[0] > box2[2] or   # self.min_x > other.max_x
                   box1[3] < box2[1] or   # self.max_y < other.min_y
                   box1[1] > box2[3])     # self.min_y > other.max_y


class Airplane(GameObject):
    """
    Player-controlled airplane
    Drawn using Bresenham's lines and midpoint algorithms
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.fuel = 100.0
        self.max_fuel = 100.0
        self.is_boosting = False
        self.base_speed = 100
        self.boost_speed = 200
        self.vertical_speed = 150
        self.color = (0.2, 0.6, 1.0)  # Sky blue
        self.body_color = (0.9, 0.9, 0.9)  # Light gray
        self.accent_color = (1.0, 0.3, 0.1)  # Orange-red
        
        # Animation
        self.propeller_angle = 0
        
        # Define airplane shape (centered at origin)
        self.body_length = 60
        self.body_height = 15
        self.wing_span = 40
        self.tail_height = 20
    
    def get_vertices(self) -> List[Tuple[float, float]]:
        """Return airplane body vertices (fuselage polygon)"""
        # Fuselage shape
        return [
            (30, 0),      # Nose
            (20, 8),      # Top front
            (-25, 8),     # Top back
            (-30, 15),    # Tail top
            (-30, -5),    # Tail bottom
            (-25, -8),    # Bottom back
            (20, -8),     # Bottom front
        ]
    
    def get_wing_vertices(self) -> List[Tuple[float, float]]:
        """Return wing vertices"""
        return [
            (5, 0),
            (15, 20),
            (-10, 20),
            (-15, 0),
        ]
    
    def get_tail_wing_vertices(self) -> List[Tuple[float, float]]:
        """Return horizontal tail wing vertices"""
        return [
            (-22, 5),
            (-18, 12),
            (-30, 12),
            (-32, 5),
        ]
    
    def get_render_data(self) -> dict:
        """
        Get all render data for the airplane
        Returns dict with different parts and their pixels
        """
        matrix = self.get_transform_matrix()
        
        data = {
            'body': [],
            'body_outline': [],
            'wings': [],
            'tail': [],
            'cockpit': [],
            'propeller': [],
            'engine': []
        }
        
        # Body (fuselage)
        body_verts = Transform2D.transform_points(self.get_vertices(), matrix)
        data['body'] = filled_polygon(body_verts)
        data['body_outline'] = self._get_polygon_outline(body_verts)
        
        # Wings (top and bottom)
        wing_verts_top = Transform2D.transform_points(self.get_wing_vertices(), matrix)
        wing_matrix_bottom = matrix @ Transform2D.scaling_matrix(1, -1)
        wing_verts_bottom = Transform2D.transform_points(self.get_wing_vertices(), wing_matrix_bottom)
        data['wings'] = filled_polygon(wing_verts_top) + filled_polygon(wing_verts_bottom)
        
        # Tail wing
        tail_verts_top = Transform2D.transform_points(self.get_tail_wing_vertices(), matrix)
        tail_matrix_bottom = matrix @ Transform2D.scaling_matrix(1, -1)
        tail_verts_bottom = Transform2D.transform_points(self.get_tail_wing_vertices(), tail_matrix_bottom)
        data['tail'] = filled_polygon(tail_verts_top) + filled_polygon(tail_verts_bottom)
        
        # Cockpit (ellipse)
        cockpit_center = Transform2D.transform_point((10, 3), matrix)
        data['cockpit'] = filled_ellipse(int(cockpit_center[0]), int(cockpit_center[1]), 8, 5)
        
        # Engine (circle)
        engine_center = Transform2D.transform_point((25, 0), matrix)
        data['engine'] = filled_circle(int(engine_center[0]), int(engine_center[1]), 6)
        
        # Propeller (rotating lines)
        self.propeller_angle += 15  # Rotate propeller
        prop_center = Transform2D.transform_point((32, 0), matrix)
        prop_length = 12
        
        for offset in [0, 90]:  # Two blades
            angle = math.radians(self.propeller_angle + offset + self.rotation)
            dx = prop_length * math.cos(angle)
            dy = prop_length * math.sin(angle)
            px, py = int(prop_center[0]), int(prop_center[1])
            data['propeller'].extend(bresenham_line(
                px - int(dx), py - int(dy),
                px + int(dx), py + int(dy)
            ))
        
        return data
    
    def _get_polygon_outline(self, vertices: List[Tuple[float, float]]) -> List[Tuple[int, int]]:
        """Get outline pixels using Bresenham's algorithm"""
        points = []
        n = len(vertices)
        for i in range(n):
            x1, y1 = int(vertices[i][0]), int(vertices[i][1])
            x2, y2 = int(vertices[(i + 1) % n][0]), int(vertices[(i + 1) % n][1])
            points.extend(bresenham_line(x1, y1, x2, y2))
        return points
    
    def update(self, dt: float, keys: dict):
        """Update airplane based on input"""
        # Vertical movement
        if keys.get('up'):
            self.velocity_y = self.vertical_speed
            self.rotation = min(self.rotation + 100 * dt, 15)  # Tilt up
        elif keys.get('down'):
            self.velocity_y = -self.vertical_speed
            self.rotation = max(self.rotation - 100 * dt, -15)  # Tilt down
        else:
            self.velocity_y *= 0.9  # Damping
            # Return to level
            if abs(self.rotation) > 0.5:
                self.rotation *= 0.95
            else:
                self.rotation = 0
        
        # Horizontal boost
        if keys.get('boost') and self.fuel > 0:
            self.is_boosting = True
            self.velocity_x = self.boost_speed
            self.fuel -= 20 * dt  # Consume fuel
        else:
            self.is_boosting = False
            self.velocity_x = self.base_speed
        
        # Natural fuel consumption
        self.fuel -= 2 * dt
        self.fuel = max(0, self.fuel)
        
        # Update position
        self.y += self.velocity_y * dt
        
        # Keep within bounds
        self.y = max(50, min(550, self.y))


class Missile(GameObject):
    """
    Enemy missile/obstacle
    Drawn using midpoint ellipse and Bresenham's lines
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.velocity_x = -random.uniform(150, 300)  # Move left
        self.velocity_y = random.uniform(-50, 50)
        self.color = (1.0, 0.2, 0.2)  # Red
        self.body_color = (0.6, 0.6, 0.6)  # Gray
        self.length = random.randint(30, 50)
        self.height = 8
        self.trail_particles = []
    
    def get_vertices(self) -> List[Tuple[float, float]]:
        """Missile body vertices - nose pointing LEFT (direction of travel)"""
        l = self.length
        h = self.height
        return [
            (-l/2, 0),       # Nose tip (pointing left)
            (-l/4, h/2),     # Top front
            (l/2, h/2),      # Top back
            (l/2 + 5, h),    # Fin top
            (l/2, 0),        # Back center
            (l/2 + 5, -h),   # Fin bottom
            (l/2, -h/2),     # Bottom back
            (-l/4, -h/2),    # Bottom front
        ]
    
    def get_render_data(self) -> dict:
        """Get render data for missile"""
        matrix = self.get_transform_matrix()
        
        data = {
            'body': [],
            'nose': [],
            'flame': [],
            'outline': []
        }
        
        # Body
        body_verts = Transform2D.transform_points(self.get_vertices(), matrix)
        data['body'] = filled_polygon(body_verts)
        data['outline'] = self._get_polygon_outline(body_verts)
        
        # Nose cone (using ellipse) - pointing left
        nose_pos = Transform2D.transform_point((-self.length/2 + 5, 0), matrix)
        data['nose'] = filled_ellipse(int(nose_pos[0]), int(nose_pos[1]), 8, 4)
        
        # Flame trail - at the back (right side)
        flame_pos = Transform2D.transform_point((self.length/2 + 5, 0), matrix)
        flame_length = random.randint(10, 20)
        for i in range(3):
            offset = random.randint(-3, 3)
            data['flame'].extend(bresenham_line(
                int(flame_pos[0]), int(flame_pos[1]),
                int(flame_pos[0] + flame_length + i*5), int(flame_pos[1] + offset)
            ))
        
        return data
    
    def _get_polygon_outline(self, vertices):
        points = []
        n = len(vertices)
        for i in range(n):
            x1, y1 = int(vertices[i][0]), int(vertices[i][1])
            x2, y2 = int(vertices[(i + 1) % n][0]), int(vertices[(i + 1) % n][1])
            points.extend(bresenham_line(x1, y1, x2, y2))
        return points
    
    def update(self, dt: float):
        super().update(dt)
        # Slight wave motion
        self.velocity_y = 30 * math.sin(self.x * 0.02)


class Cloud(GameObject):
    """
    Background cloud decoration
    Drawn using midpoint circles
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.velocity_x = -random.uniform(20, 50)  # Slow drift left
        self.color = (1.0, 1.0, 1.0)  # White
        self.alpha = random.uniform(0.3, 0.7)
        self.circles = self._generate_cloud_shape()
    
    def _generate_cloud_shape(self) -> List[Tuple[int, int, int]]:
        """Generate random cloud shape as collection of circles (x, y, r)"""
        circles = []
        num_circles = random.randint(3, 6)
        
        for i in range(num_circles):
            cx = random.randint(-30, 30)
            cy = random.randint(-10, 10)
            r = random.randint(15, 30)
            circles.append((cx, cy, r))
        
        return circles
    
    def get_render_data(self) -> dict:
        """Get render data for cloud"""
        data = {'circles': []}
        
        for cx, cy, r in self.circles:
            world_x = int(self.x + cx)
            world_y = int(self.y + cy)
            data['circles'].extend(filled_circle(world_x, world_y, r))
        
        return data


class FuelCanister(GameObject):
    """
    Collectible fuel canister
    Drawn using rectangles and circles
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.velocity_x = -100
        self.color = (0.2, 1.0, 0.2)  # Green
        self.fuel_amount = 25
        self.bob_offset = 0
        self.bob_speed = 5
    
    def get_vertices(self) -> List[Tuple[float, float]]:
        """Canister body"""
        return [
            (-10, -15),
            (10, -15),
            (10, 15),
            (-10, 15),
        ]
    
    def get_render_data(self) -> dict:
        matrix = self.get_transform_matrix()
        
        # Add bobbing motion
        self.bob_offset = 5 * math.sin(self.x * 0.05)
        bob_matrix = Transform2D.translation_matrix(0, self.bob_offset)
        matrix = matrix @ bob_matrix
        
        data = {
            'body': [],
            'cap': [],
            'symbol': []
        }
        
        # Body
        body_verts = Transform2D.transform_points(self.get_vertices(), matrix)
        data['body'] = filled_polygon(body_verts)
        
        # Cap (circle on top)
        cap_pos = Transform2D.transform_point((0, -18), matrix)
        data['cap'] = filled_circle(int(cap_pos[0]), int(cap_pos[1]), 6)
        
        # Plus symbol for fuel
        center = Transform2D.transform_point((0, 0), matrix)
        cx, cy = int(center[0]), int(center[1])
        data['symbol'].extend(bresenham_line(cx - 5, cy, cx + 5, cy))
        data['symbol'].extend(bresenham_line(cx, cy - 5, cx, cy + 5))
        
        return data
    
    def update(self, dt: float):
        super().update(dt)


class Star(GameObject):
    """
    Background star for parallax effect
    """
    
    def __init__(self, x: float, y: float, layer: int = 0):
        super().__init__(x, y)
        self.layer = layer  # 0 = far, 1 = mid, 2 = near
        self.velocity_x = -20 * (layer + 1)  # Parallax speed
        self.brightness = random.uniform(0.3, 1.0)
        self.size = random.randint(1, 2 + layer)
        self.twinkle_phase = random.uniform(0, 2 * math.pi)
    
    def get_render_data(self) -> dict:
        # Twinkle effect
        twinkle = 0.5 + 0.5 * math.sin(self.twinkle_phase)
        self.twinkle_phase += 0.1
        
        data = {'points': []}
        
        if self.size == 1:
            data['points'] = [(int(self.x), int(self.y))]
        else:
            data['points'] = filled_circle(int(self.x), int(self.y), self.size)
        
        data['brightness'] = self.brightness * twinkle
        return data


class Explosion(GameObject):
    """
    Explosion effect when missile hits or plane crashes
    """
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.lifetime = 0.5  # seconds
        self.age = 0
        self.particles = []
        self._generate_particles()
    
    def _generate_particles(self):
        """Generate explosion particles"""
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200)
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'vx': speed * math.cos(angle),
                'vy': speed * math.sin(angle),
                'size': random.randint(2, 6),
                'color': random.choice([
                    (1.0, 0.8, 0.0),   # Yellow
                    (1.0, 0.5, 0.0),   # Orange
                    (1.0, 0.2, 0.0),   # Red-orange
                    (1.0, 1.0, 1.0),   # White
                ])
            })
    
    def update(self, dt: float):
        self.age += dt
        if self.age >= self.lifetime:
            self.active = False
            return
        
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vy'] -= 200 * dt  # Gravity
            p['size'] = max(1, p['size'] - 5 * dt)
    
    def get_render_data(self) -> dict:
        data = {'particles': []}
        
        alpha = 1.0 - (self.age / self.lifetime)
        
        for p in self.particles:
            if p['size'] >= 1:
                points = filled_circle(int(p['x']), int(p['y']), int(p['size']))
                data['particles'].append({
                    'points': points,
                    'color': p['color'],
                    'alpha': alpha
                })
        
        return data


class Ground(GameObject):
    """
    Scrolling ground with terrain
    """
    
    def __init__(self, width: int, height: int):
        super().__init__(0, 0)
        self.width = width
        self.ground_height = height
        self.terrain_points = self._generate_terrain()
        self.scroll_x = 0
    
    def _generate_terrain(self) -> List[Tuple[float, float]]:
        """Generate terrain height map"""
        points = []
        x = 0
        while x < self.width * 2:
            # Simple sine wave terrain
            y = 30 + 15 * math.sin(x * 0.02) + 10 * math.sin(x * 0.05)
            points.append((x, y))
            x += 10
        return points
    
    def get_render_data(self) -> dict:
        data = {'ground': [], 'grass': []}
        
        # Create ground polygon
        visible_points = []
        for px, py in self.terrain_points:
            screen_x = px - self.scroll_x
            if -50 < screen_x < self.width + 50:
                visible_points.append((screen_x, py))
        
        if len(visible_points) >= 2:
            # Close the polygon at the bottom
            ground_poly = visible_points + [
                (visible_points[-1][0], 0),
                (visible_points[0][0], 0)
            ]
            data['ground'] = filled_polygon(ground_poly)
            
            # Grass line on top
            for i in range(len(visible_points) - 1):
                x1, y1 = int(visible_points[i][0]), int(visible_points[i][1])
                x2, y2 = int(visible_points[i+1][0]), int(visible_points[i+1][1])
                data['grass'].extend(bresenham_line(x1, y1, x2, y2))
        
        return data
    
    def update(self, dt: float, speed: float):
        self.scroll_x += speed * dt
        # Wrap terrain
        if self.scroll_x > self.width:
            self.scroll_x -= self.width
