"""
Computer Graphics Algorithms Module
Implements: Bresenham's Line, Midpoint Circle/Ellipse, Transformations, Clipping
"""

import numpy as np
from typing import List, Tuple

# ============================================================================
# BRESENHAM'S LINE DRAWING ALGORITHM
# ============================================================================

def bresenham_line(x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
    """
    Bresenham's Line Drawing Algorithm
    Returns list of (x, y) pixel coordinates forming a line from (x1,y1) to (x2,y2)
    """
    points = []
    
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    
    x, y = x1, y1
    
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    
    if dx > dy:
        # Slope < 1
        p = 2 * dy - dx
        for _ in range(dx + 1):
            points.append((x, y))
            if p >= 0:
                y += sy
                p -= 2 * dx
            p += 2 * dy
            x += sx
    else:
        # Slope >= 1
        p = 2 * dx - dy
        for _ in range(dy + 1):
            points.append((x, y))
            if p >= 0:
                x += sx
                p -= 2 * dy
            p += 2 * dx
            y += sy
    
    return points


# ============================================================================
# MIDPOINT CIRCLE ALGORITHM
# ============================================================================

def midpoint_circle(xc: int, yc: int, r: int) -> List[Tuple[int, int]]:
    """
    Midpoint Circle Algorithm
    Returns list of (x, y) pixel coordinates forming a circle centered at (xc, yc) with radius r
    """
    points = []
    
    def plot_circle_points(xc, yc, x, y):
        """Plot all 8 symmetric points of the circle"""
        points.extend([
            (xc + x, yc + y), (xc - x, yc + y),
            (xc + x, yc - y), (xc - x, yc - y),
            (xc + y, yc + x), (xc - y, yc + x),
            (xc + y, yc - x), (xc - y, yc - x)
        ])
    
    x = 0
    y = r
    p = 1 - r  # Initial decision parameter
    
    plot_circle_points(xc, yc, x, y)
    
    while x < y:
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1
        plot_circle_points(xc, yc, x, y)
    
    return points


def filled_circle(xc: int, yc: int, r: int) -> List[Tuple[int, int]]:
    """
    Filled circle using midpoint algorithm with horizontal line filling
    """
    points = []
    
    def draw_horizontal_line(x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            points.append((x, y))
    
    x = 0
    y = r
    p = 1 - r
    
    while x <= y:
        draw_horizontal_line(xc - x, xc + x, yc + y)
        draw_horizontal_line(xc - x, xc + x, yc - y)
        draw_horizontal_line(xc - y, xc + y, yc + x)
        draw_horizontal_line(xc - y, xc + y, yc - x)
        
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1
    
    return list(set(points))  # Remove duplicates


# ============================================================================
# MIDPOINT ELLIPSE ALGORITHM
# ============================================================================

def midpoint_ellipse(xc: int, yc: int, rx: int, ry: int) -> List[Tuple[int, int]]:
    """
    Midpoint Ellipse Algorithm
    Returns list of (x, y) pixel coordinates forming an ellipse
    centered at (xc, yc) with semi-axes rx and ry
    """
    points = []
    
    def plot_ellipse_points(xc, yc, x, y):
        """Plot all 4 symmetric points of the ellipse"""
        points.extend([
            (xc + x, yc + y), (xc - x, yc + y),
            (xc + x, yc - y), (xc - x, yc - y)
        ])
    
    rx2 = rx * rx
    ry2 = ry * ry
    two_rx2 = 2 * rx2
    two_ry2 = 2 * ry2
    
    # Region 1
    x = 0
    y = ry
    px = 0
    py = two_rx2 * y
    
    plot_ellipse_points(xc, yc, x, y)
    
    # Region 1: dy/dx > -1
    p1 = ry2 - (rx2 * ry) + (0.25 * rx2)
    while px < py:
        x += 1
        px += two_ry2
        if p1 < 0:
            p1 += ry2 + px
        else:
            y -= 1
            py -= two_rx2
            p1 += ry2 + px - py
        plot_ellipse_points(xc, yc, x, y)
    
    # Region 2: dy/dx < -1
    p2 = ry2 * (x + 0.5) ** 2 + rx2 * (y - 1) ** 2 - rx2 * ry2
    while y > 0:
        y -= 1
        py -= two_rx2
        if p2 > 0:
            p2 += rx2 - py
        else:
            x += 1
            px += two_ry2
            p2 += rx2 - py + px
        plot_ellipse_points(xc, yc, x, y)
    
    return points


def filled_ellipse(xc: int, yc: int, rx: int, ry: int) -> List[Tuple[int, int]]:
    """
    Filled ellipse using midpoint algorithm
    """
    points = []
    
    def draw_horizontal_line(x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            points.append((x, y))
    
    rx2 = rx * rx
    ry2 = ry * ry
    two_rx2 = 2 * rx2
    two_ry2 = 2 * ry2
    
    x = 0
    y = ry
    px = 0
    py = two_rx2 * y
    
    # Region 1
    p1 = ry2 - (rx2 * ry) + (0.25 * rx2)
    while px < py:
        draw_horizontal_line(xc - x, xc + x, yc + y)
        draw_horizontal_line(xc - x, xc + x, yc - y)
        x += 1
        px += two_ry2
        if p1 < 0:
            p1 += ry2 + px
        else:
            y -= 1
            py -= two_rx2
            p1 += ry2 + px - py
    
    # Region 2
    p2 = ry2 * (x + 0.5) ** 2 + rx2 * (y - 1) ** 2 - rx2 * ry2
    while y >= 0:
        draw_horizontal_line(xc - x, xc + x, yc + y)
        draw_horizontal_line(xc - x, xc + x, yc - y)
        y -= 1
        py -= two_rx2
        if p2 > 0:
            p2 += rx2 - py
        else:
            x += 1
            px += two_ry2
            p2 += rx2 - py + px
    
    return list(set(points))


# ============================================================================
# HOMOGENEOUS 2D TRANSFORMATION MATRICES (Homogeneity Factor = 1)
# ============================================================================

class Transform2D:
    """
    2D Transformations using Homogeneous Coordinates
    All matrices use homogeneity factor = 1
    Point representation: [x, y, 1]^T
    """
    
    @staticmethod
    def translation_matrix(tx: float, ty: float) -> np.ndarray:
        """
        Create 3x3 translation matrix
        | 1  0  tx |
        | 0  1  ty |
        | 0  0  1  |
        """
        return np.array([
            [1, 0, tx],
            [0, 1, ty],
            [0, 0, 1]
        ], dtype=float)
    
    @staticmethod
    def scaling_matrix(sx: float, sy: float) -> np.ndarray:
        """
        Create 3x3 scaling matrix
        | sx  0  0 |
        | 0  sy  0 |
        | 0   0  1 |
        """
        return np.array([
            [sx, 0, 0],
            [0, sy, 0],
            [0, 0, 1]
        ], dtype=float)
    
    @staticmethod
    def rotation_matrix(angle_degrees: float) -> np.ndarray:
        """
        Create 3x3 rotation matrix (counter-clockwise)
        | cos(θ)  -sin(θ)  0 |
        | sin(θ)   cos(θ)  0 |
        |   0        0     1 |
        """
        theta = np.radians(angle_degrees)
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)
        return np.array([
            [cos_t, -sin_t, 0],
            [sin_t, cos_t, 0],
            [0, 0, 1]
        ], dtype=float)
    
    @staticmethod
    def rotation_about_point(angle_degrees: float, px: float, py: float) -> np.ndarray:
        """
        Rotate about an arbitrary point (px, py)
        T(-px,-py) * R(θ) * T(px,py)
        """
        T1 = Transform2D.translation_matrix(-px, -py)
        R = Transform2D.rotation_matrix(angle_degrees)
        T2 = Transform2D.translation_matrix(px, py)
        return T2 @ R @ T1
    
    @staticmethod
    def scaling_about_point(sx: float, sy: float, px: float, py: float) -> np.ndarray:
        """
        Scale about an arbitrary point (px, py)
        """
        T1 = Transform2D.translation_matrix(-px, -py)
        S = Transform2D.scaling_matrix(sx, sy)
        T2 = Transform2D.translation_matrix(px, py)
        return T2 @ S @ T1
    
    @staticmethod
    def shear_matrix(shx: float, shy: float) -> np.ndarray:
        """
        Create 3x3 shear matrix
        | 1   shx  0 |
        | shy  1   0 |
        | 0    0   1 |
        """
        return np.array([
            [1, shx, 0],
            [shy, 1, 0],
            [0, 0, 1]
        ], dtype=float)
    
    @staticmethod
    def reflect_x() -> np.ndarray:
        """Reflection about x-axis"""
        return Transform2D.scaling_matrix(1, -1)
    
    @staticmethod
    def reflect_y() -> np.ndarray:
        """Reflection about y-axis"""
        return Transform2D.scaling_matrix(-1, 1)
    
    @staticmethod
    def reflect_origin() -> np.ndarray:
        """Reflection about origin"""
        return Transform2D.scaling_matrix(-1, -1)
    
    @staticmethod
    def transform_point(point: Tuple[float, float], matrix: np.ndarray) -> Tuple[float, float]:
        """
        Transform a 2D point using homogeneous matrix
        """
        p = np.array([point[0], point[1], 1])
        result = matrix @ p
        return (result[0] / result[2], result[1] / result[2])
    
    @staticmethod
    def transform_points(points: List[Tuple[float, float]], matrix: np.ndarray) -> List[Tuple[float, float]]:
        """
        Transform multiple 2D points using homogeneous matrix
        """
        return [Transform2D.transform_point(p, matrix) for p in points]


# ============================================================================
# COHEN-SUTHERLAND LINE CLIPPING ALGORITHM
# ============================================================================

class CohenSutherland:
    """
    Cohen-Sutherland Line Clipping Algorithm
    Clips lines against a rectangular clipping window
    """
    
    # Region codes
    INSIDE = 0  # 0000
    LEFT = 1    # 0001
    RIGHT = 2   # 0010
    BOTTOM = 4  # 0100
    TOP = 8     # 1000
    
    def __init__(self, x_min: float, y_min: float, x_max: float, y_max: float):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
    
    def compute_code(self, x: float, y: float) -> int:
        """Compute the region code for a point"""
        code = self.INSIDE
        
        if x < self.x_min:
            code |= self.LEFT
        elif x > self.x_max:
            code |= self.RIGHT
        
        if y < self.y_min:
            code |= self.BOTTOM
        elif y > self.y_max:
            code |= self.TOP
        
        return code
    
    def clip_line(self, x1: float, y1: float, x2: float, y2: float) -> Tuple[bool, Tuple[float, float, float, float]]:
        """
        Clip a line segment against the clipping window
        Returns: (accepted, (x1, y1, x2, y2))
        """
        code1 = self.compute_code(x1, y1)
        code2 = self.compute_code(x2, y2)
        
        while True:
            if (code1 | code2) == 0:
                # Both points inside - trivially accept
                return True, (x1, y1, x2, y2)
            
            elif (code1 & code2) != 0:
                # Both points share an outside region - trivially reject
                return False, (0, 0, 0, 0)
            
            else:
                # Line needs clipping
                # Pick an outside point
                code_out = code1 if code1 != 0 else code2
                
                # Find intersection point
                if code_out & self.TOP:
                    x = x1 + (x2 - x1) * (self.y_max - y1) / (y2 - y1)
                    y = self.y_max
                elif code_out & self.BOTTOM:
                    x = x1 + (x2 - x1) * (self.y_min - y1) / (y2 - y1)
                    y = self.y_min
                elif code_out & self.RIGHT:
                    y = y1 + (y2 - y1) * (self.x_max - x1) / (x2 - x1)
                    x = self.x_max
                elif code_out & self.LEFT:
                    y = y1 + (y2 - y1) * (self.x_min - x1) / (x2 - x1)
                    x = self.x_min
                
                # Replace outside point with intersection point
                if code_out == code1:
                    x1, y1 = x, y
                    code1 = self.compute_code(x1, y1)
                else:
                    x2, y2 = x, y
                    code2 = self.compute_code(x2, y2)


# ============================================================================
# SUTHERLAND-HODGMAN POLYGON CLIPPING ALGORITHM
# ============================================================================

class SutherlandHodgman:
    """
    Sutherland-Hodgman Polygon Clipping Algorithm
    Clips polygons against a rectangular clipping window
    """
    
    def __init__(self, x_min: float, y_min: float, x_max: float, y_max: float):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
    
    def _clip_edge(self, polygon: List[Tuple[float, float]], 
                   edge_start: Tuple[float, float], 
                   edge_end: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Clip polygon against a single edge"""
        
        def inside(p):
            """Check if point is inside the edge (left side)"""
            return ((edge_end[0] - edge_start[0]) * (p[1] - edge_start[1]) - 
                    (edge_end[1] - edge_start[1]) * (p[0] - edge_start[0])) >= 0
        
        def intersection(p1, p2):
            """Find intersection of line p1-p2 with edge"""
            x1, y1 = p1
            x2, y2 = p2
            x3, y3 = edge_start
            x4, y4 = edge_end
            
            denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if abs(denom) < 1e-10:
                return p1
            
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
            
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return (x, y)
        
        if len(polygon) == 0:
            return []
        
        output = []
        
        for i in range(len(polygon)):
            current = polygon[i]
            next_vertex = polygon[(i + 1) % len(polygon)]
            
            current_inside = inside(current)
            next_inside = inside(next_vertex)
            
            if current_inside:
                if next_inside:
                    # Both inside - add next
                    output.append(next_vertex)
                else:
                    # Current inside, next outside - add intersection
                    output.append(intersection(current, next_vertex))
            else:
                if next_inside:
                    # Current outside, next inside - add intersection and next
                    output.append(intersection(current, next_vertex))
                    output.append(next_vertex)
                # Both outside - add nothing
        
        return output
    
    def clip_polygon(self, polygon: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Clip polygon against all four edges of the clipping window
        """
        # Define the four edges of the clipping window (counter-clockwise)
        edges = [
            ((self.x_min, self.y_min), (self.x_max, self.y_min)),  # Bottom
            ((self.x_max, self.y_min), (self.x_max, self.y_max)),  # Right
            ((self.x_max, self.y_max), (self.x_min, self.y_max)),  # Top
            ((self.x_min, self.y_max), (self.x_min, self.y_min)),  # Left
        ]
        
        output = polygon[:]
        
        for edge_start, edge_end in edges:
            if len(output) == 0:
                break
            output = self._clip_edge(output, edge_start, edge_end)
        
        return output


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def polygon_from_lines(vertices: List[Tuple[float, float]]) -> List[Tuple[int, int]]:
    """
    Generate all pixel points for a polygon using Bresenham's line algorithm
    """
    points = []
    n = len(vertices)
    for i in range(n):
        x1, y1 = int(vertices[i][0]), int(vertices[i][1])
        x2, y2 = int(vertices[(i + 1) % n][0]), int(vertices[(i + 1) % n][1])
        points.extend(bresenham_line(x1, y1, x2, y2))
    return points


def filled_polygon(vertices: List[Tuple[float, float]]) -> List[Tuple[int, int]]:
    """
    Fill a polygon using scanline algorithm
    """
    if len(vertices) < 3:
        return []
    
    points = []
    
    # Find bounding box
    min_y = int(min(v[1] for v in vertices))
    max_y = int(max(v[1] for v in vertices))
    
    # Scanline fill
    for y in range(min_y, max_y + 1):
        intersections = []
        n = len(vertices)
        
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % n]
            
            if y1 == y2:
                continue
            
            if min(y1, y2) <= y < max(y1, y2):
                x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                intersections.append(x)
        
        intersections.sort()
        
        for i in range(0, len(intersections) - 1, 2):
            x_start = int(intersections[i])
            x_end = int(intersections[i + 1])
            for x in range(x_start, x_end + 1):
                points.append((x, y))
    
    return points
