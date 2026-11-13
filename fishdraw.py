"""
FishDraw - Procedurally generated fish drawings
Ported from JavaScript to Python for Badger2040 e-ink display
"""

import math
import random
from typing import List, Tuple, Optional, Callable, Dict, Any

# Constants and types
PI = math.pi
Point = Tuple[float, float]
Polyline = List[Point]
Polylines = List[Polyline]

# Random number generation with seeded XOR shift
jsr = 0x5EED

def set_seed(seed: int):
    """Set the random seed"""
    global jsr
    jsr = seed & 0xFFFFFFFF

def rand() -> float:
    """Pseudo-random number generator (XOR shift)"""
    global jsr
    jsr ^= (jsr << 17) & 0xFFFFFFFF
    jsr ^= (jsr >> 13) & 0xFFFFFFFF
    jsr ^= (jsr << 5) & 0xFFFFFFFF
    return (jsr & 0xFFFFFFFF) / 4294967295.0

# Perlin noise implementation
PERLIN_YWRAPB = 4
PERLIN_YWRAP = 1 << PERLIN_YWRAPB
PERLIN_ZWRAPB = 8
PERLIN_ZWRAP = 1 << PERLIN_ZWRAPB
PERLIN_SIZE = 4095
perlin_octaves = 4
perlin_amp_falloff = 0.5
perlin = None

def scaled_cosine(i: float) -> float:
    """Cosine interpolation function for Perlin noise"""
    return 0.5 * (1.0 - math.cos(i * PI))

def noise(x: float, y: float = 0, z: float = 0) -> float:
    """Perlin noise function"""
    global perlin
    
    y = y or 0
    z = z or 0
    
    if perlin is None:
        perlin = [rand() for _ in range(PERLIN_SIZE + 1)]
    
    x = abs(x)
    y = abs(y)
    z = abs(z)
    
    xi = int(x)
    yi = int(y)
    zi = int(z)
    
    xf = x - xi
    yf = y - yi
    zf = z - zi
    
    r = 0
    ampl = 0.5
    
    for o in range(perlin_octaves):
        of = xi + (yi << PERLIN_YWRAPB) + (zi << PERLIN_ZWRAPB)
        rxf = scaled_cosine(xf)
        ryf = scaled_cosine(yf)
        
        n1 = perlin[of & PERLIN_SIZE]
        n1 += rxf * (perlin[(of + 1) & PERLIN_SIZE] - n1)
        
        n2 = perlin[(of + PERLIN_YWRAP) & PERLIN_SIZE]
        n2 += rxf * (perlin[(of + PERLIN_YWRAP + 1) & PERLIN_SIZE] - n2)
        
        n1 += ryf * (n2 - n1)
        
        of += PERLIN_ZWRAP
        n2 = perlin[of & PERLIN_SIZE]
        n2 += rxf * (perlin[(of + 1) & PERLIN_SIZE] - n2)
        
        n3 = perlin[(of + PERLIN_YWRAP) & PERLIN_SIZE]
        n3 += rxf * (perlin[(of + PERLIN_YWRAP + 1) & PERLIN_SIZE] - n3)
        
        n2 += ryf * (n3 - n2)
        n1 += scaled_cosine(zf) * (n2 - n1)
        
        r += n1 * ampl
        ampl *= perlin_amp_falloff
        
        xi <<= 1
        xf *= 2
        yi <<= 1
        yf *= 2
        zi <<= 1
        zf *= 2
        
        if xf >= 1.0:
            xi += 1
            xf -= 1
        if yf >= 1.0:
            yi += 1
            yf -= 1
        if zf >= 1.0:
            zi += 1
            zf -= 1
    
    return r

def dist(x0: float, y0: float, x1: float, y1: float) -> float:
    """Euclidean distance"""
    return math.hypot(x1 - x0, y1 - y0)

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation"""
    return a * (1 - t) + b * t

def lerp2d(x0: float, y0: float, x1: float, y1: float, t: float) -> Point:
    """2D linear interpolation"""
    return (
        x0 * (1 - t) + x1 * t,
        y0 * (1 - t) + y1 * t,
    )

def get_bbox(points: Polyline) -> Dict[str, float]:
    """Get bounding box of points"""
    xmin = float('inf')
    ymin = float('inf')
    xmax = float('-inf')
    ymax = float('-inf')
    
    for x, y in points:
        xmin = min(xmin, x)
        ymin = min(ymin, y)
        xmax = max(xmax, x)
        ymax = max(ymax, y)
    
    return {'x': xmin, 'y': ymin, 'w': xmax - xmin, 'h': ymax - ymin}

def seg_isect(p0x: float, p0y: float, p1x: float, p1y: float,
              q0x: float, q0y: float, q1x: float, q1y: float,
              is_ray: bool = False) -> Optional[Dict]:
    """Segment intersection"""
    d0x = p1x - p0x
    d0y = p1y - p0y
    d1x = q1x - q0x
    d1y = q1y - q0y
    
    vc = d0x * d1y - d0y * d1x
    if vc == 0:
        return None
    
    vcn = vc * vc
    q0x_p0x = q0x - p0x
    q0y_p0y = q0y - p0y
    vc_vcn = vc / vcn
    
    t = (q0x_p0x * d1y - q0y_p0y * d1x) * vc_vcn
    s = (q0x_p0x * d0y - q0y_p0y * d0x) * vc_vcn
    
    if 0 <= t and (is_ray or t < 1) and 0 <= s and s < 1:
        ret = {'t': t, 's': s, 'side': None, 'other': None, 'xy': None}
        ret['xy'] = (p1x * t + p0x * (1 - t), p1y * t + p0y * (1 - t))
        ret['side'] = 1 if pt_in_pl(p0x, p0y, p1x, p1y, q0x, q0y) < 0 else -1
        return ret
    
    return None

def pt_in_pl(x: float, y: float, x0: float, y0: float, x1: float, y1: float) -> float:
    """Point in line test"""
    dx = x1 - x0
    dy = y1 - y0
    e = (x - x0) * dy - (y - y0) * dx
    return e

def poly_bridge(poly0: Polyline, poly1: Polyline) -> Polyline:
    """Connect two polygons with a bridge"""
    dmin = float('inf')
    imin = None
    
    for i in range(len(poly0)):
        for j in range(len(poly1)):
            x0, y0 = poly0[i]
            x1, y1 = poly1[j]
            dx = x0 - x1
            dy = y0 - y1
            d2 = dx * dx + dy * dy
            if d2 < dmin:
                dmin = d2
                imin = (i, j)
    
    u = (poly0[:imin[0]] + poly1[imin[1]:] + 
         poly1[:imin[1]] + poly0[imin[0]:])
    return u

def distsq(x0: float, y0: float, x1: float, y1: float) -> float:
    """Distance squared"""
    return (x1 - x0) ** 2 + (y1 - y0) ** 2

def pt_seg_dist(p: Point, p0: Point, p1: Point) -> float:
    """Point to segment distance"""
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    len2 = dx * dx + dy * dy
    
    if len2 == 0:
        return dist(p[0], p[1], p0[0], p0[1])
    
    t = max(0, min(1, ((p[0] - p0[0]) * dx + (p[1] - p0[1]) * dy) / len2))
    
    proj = (p0[0] + t * dx, p0[1] + t * dy)
    return dist(p[0], p[1], proj[0], proj[1])

def approx_poly_dp(polyline: Polyline, epsilon: float) -> Polyline:
    """Simplify polyline using Douglas-Peucker algorithm"""
    if len(polyline) <= 2:
        return polyline
    
    dmax = 0
    index = 0
    for i in range(1, len(polyline) - 1):
        d = pt_seg_dist(polyline[i], polyline[0], polyline[-1])
        if d > dmax:
            dmax = d
            index = i
    
    if dmax > epsilon:
        rec1 = approx_poly_dp(polyline[:index + 1], epsilon)
        rec2 = approx_poly_dp(polyline[index:], epsilon)
        return rec1[:-1] + rec2
    else:
        return [polyline[0], polyline[-1]]

def resample(polyline: Polyline, step: float) -> Polyline:
    """Resample polyline with fixed step size"""
    if len(polyline) < 2:
        return polyline
    
    out = []
    step_dist = 0
    prev = polyline[0]
    out.append(prev)
    
    for i in range(1, len(polyline)):
        curr = polyline[i]
        segment_dist = dist(prev[0], prev[1], curr[0], curr[1])
        
        if segment_dist == 0:
            continue
        
        step_dist += segment_dist
        
        # Add intermediate points
        while step_dist >= step:
            frac = (step - (step_dist - segment_dist)) / segment_dist
            x = prev[0] + (curr[0] - prev[0]) * frac
            y = prev[1] + (curr[1] - prev[1]) * frac
            out.append((x, y))
            step_dist -= step
        
        prev = curr
    
    # Always add the last point
    if out[-1] != polyline[-1]:
        out.append(polyline[-1])
    
    return out

def shade_shape(poly: Polyline, step: float = 5, dx: float = 10, dy: float = 20) -> Polylines:
    """Create shading lines for a polygon"""
    bbox = get_bbox(poly)
    out = []
    
    y = bbox['y']
    while y < bbox['y'] + bbox['h']:
        line = [
            (bbox['x'], y),
            (bbox['x'] + bbox['w'], y)
        ]
        clipped = clip_poly_by_line(poly, line)
        if clipped:
            out.append(clipped)
        y += step
    
    return out

def trsl_poly(poly: Polyline, x: float, y: float) -> Polyline:
    """Translate polygon"""
    return [(px + x, py + y) for px, py in poly]

def scl_poly(poly: Polyline, sx: float, sy: float) -> Polyline:
    """Scale polygon"""
    return [(px * sx, py * sy) for px, py in poly]

def shr_poly(poly: Polyline, sx: float) -> Polyline:
    """Shear polygon"""
    return [(px + py * sx, py) for px, py in poly]

def rot_poly(poly: Polyline, th: float) -> Polyline:
    """Rotate polygon"""
    cos_th = math.cos(th)
    sin_th = math.sin(th)
    return [
        (px * cos_th - py * sin_th, px * sin_th + py * cos_th)
        for px, py in poly
    ]

def pow(a: float, b: float) -> float:
    """Power function"""
    return a ** b

def gauss2d(x: float, y: float) -> float:
    """2D Gaussian function"""
    return math.exp(-(x * x + y * y) / 2)

def clip_poly_by_line(poly: Polyline, line: Polyline) -> Optional[Polyline]:
    """Clip polygon by line (simple version)"""
    # Simplified clipping - just return the polygon if it's valid
    return poly if len(poly) >= 3 else None

# Fish generation parameters
default_params = {
    'body_type': 0,
    'tail_type': 0,
    'body_color': 0,
    'fin_type': 0,
    'eye_type': 0,
    'pattern': 0,
}

def generate_params() -> Dict:
    """Generate random fish parameters"""
    params = default_params.copy()
    params['body_type'] = int(rand() * 3)
    params['tail_type'] = int(rand() * 3)
    params['body_color'] = int(rand() * 5)
    params['fin_type'] = int(rand() * 3)
    params['eye_type'] = int(rand() * 2)
    params['pattern'] = int(rand() * 4)
    return params

def fish_body_simple(scale: float = 1) -> Tuple[Polyline, Polylines]:
    """Generate simple fish body"""
    # Create a simple ellipse-like body
    n = 20
    body = []
    for i in range(n):
        t = i / (n - 1)
        a = t * PI
        x = (math.cos(a) - 0.5) * scale * 100
        y = math.sin(a) * scale * 50
        body.append((x, y))
    
    return body, [body]

def fish(params: Dict) -> Polylines:
    """Generate fish drawing"""
    polylines = []
    
    # Generate body
    body, body_lines = fish_body_simple(1.5)
    polylines.extend(body_lines)
    
    # Generate tail
    tail = trsl_poly([(i * 10 - 50, (rand() - 0.5) * 20) for i in range(10)], 150, 0)
    polylines.append(tail)
    
    # Generate fins
    for i in range(3):
        fin = [(rand() * 20 - 10, i * 30 - 30), (rand() * 10, i * 30)]
        polylines.append(fin)
    
    # Generate eye
    eye = []
    for i in range(8):
        a = i / 8 * PI * 2
        eye.append((-80 + math.cos(a) * 10, math.sin(a) * 10))
    polylines.append(eye)
    
    return polylines

def reframe(drawing: Polylines, margin: float = 20, name: str = "Fish") -> Polylines:
    """Reframe drawing with margins"""
    bbox = get_bbox([pt for polyline in drawing for pt in polyline])
    
    # Translate to origin with margin
    offset_x = -bbox['x'] + margin
    offset_y = -bbox['y'] + margin
    
    return [trsl_poly(polyline, offset_x, offset_y) for polyline in drawing]

def cleanup(drawing: Polylines) -> Polylines:
    """Clean up drawing"""
    return drawing

def str_to_seed(s: str) -> int:
    """Convert string to seed"""
    n = 1
    for i, c in enumerate(s):
        x = ord(c) + 1
        n ^= x << (7 + (i % 5))
        n ^= (n << 17) & 0xFFFFFFFF
        n ^= (n >> 13) & 0xFFFFFFFF
        n ^= (n << 5) & 0xFFFFFFFF
        n = n & 0xFFFFFFFF
    return n

def binomen() -> str:
    """Generate random Latin-ish fish name"""
    consonants = "bcdfghjklmnprstvwxyz"
    vowels = "aeiou"
    
    genus = ""
    for i in range(int(rand() * 2) + 2):
        if rand() > 0.5:
            genus += random.choice(consonants)
        else:
            genus += random.choice(vowels)
    
    species = ""
    for i in range(int(rand() * 2) + 2):
        if rand() > 0.5:
            species += random.choice(consonants)
        else:
            species += random.choice(vowels)
    
    return genus.capitalize() + " " + species

def main(seed: Optional[str] = None) -> Polylines:
    """Main function to generate fish"""
    global jsr
    
    if seed is None:
        jsr = int(rand() * 10000)
        name = binomen()
        seed = name
    
    jsr = str_to_seed(seed)
    drawing = fish(generate_params())
    return reframe(cleanup(drawing), 20, seed + '.')

if __name__ == "__main__":
    # Test the fish generation
    drawing = main("TestFish")
    print(f"Generated {len(drawing)} polylines")
    for i, polyline in enumerate(drawing):
        print(f"  Polyline {i}: {len(polyline)} points")
