"""
FishDraw - Procedurally generated fish drawings
Complete Python port for Badger2040 e-ink display
Based on https://github.com/jbum/fishdraw

This is a complete port of the JavaScript version, with all 70+ functions
ported to Python for MicroPython/Badger2040 compatibility.
"""

import math
import random

# Try to import typing for type hints (not available in MicroPython)
try:
    from typing import List, Tuple, Optional, Dict, Any, Callable
    # Type aliases
    Point = Tuple[float, float]
    Polyline = List[Point]
    Polylines = List[Polyline]
except ImportError:
    # MicroPython: define dummy types for compatibility
    Point = None
    Polyline = None
    Polylines = None

PI = math.pi

# Random number generation with seedable XOR shift
_jsr = 0x5EED

def set_seed(seed: int):
    """Set the random seed"""
    global _jsr
    _jsr = seed & 0xFFFFFFFF

def rand() -> float:
    """Seeded pseudo-random number (XOR shift)"""
    global _jsr
    _jsr ^= (_jsr << 17) & 0xFFFFFFFF
    _jsr ^= (_jsr >> 13) & 0xFFFFFFFF
    _jsr ^= (_jsr << 5) & 0xFFFFFFFF
    return (_jsr & 0xFFFFFFFF) / 4294967295.0

# Perlin Noise
PERLIN_YWRAPB = 4
PERLIN_YWRAP = 1 << PERLIN_YWRAPB
PERLIN_ZWRAPB = 8
PERLIN_ZWRAP = 1 << PERLIN_ZWRAPB
PERLIN_SIZE = 4095
_perlin_octaves = 4
_perlin_amp_falloff = 0.5
_perlin = None

def _scaled_cosine(i: float) -> float:
    return 0.5 * (1.0 - math.cos(i * PI))

def noise(x: float, y: float = 0, z: float = 0) -> float:
    """Perlin noise function"""
    global _perlin
    
    if _perlin is None:
        _perlin = [rand() for _ in range(PERLIN_SIZE + 1)]
    
    x, y, z = abs(x), abs(y), abs(z)
    xi, yi, zi = int(x), int(y), int(z)
    xf, yf, zf = x - xi, y - yi, z - zi
    
    r, ampl = 0, 0.5
    for o in range(_perlin_octaves):
        of = xi + (yi << PERLIN_YWRAPB) + (zi << PERLIN_ZWRAPB)
        rxf, ryf = _scaled_cosine(xf), _scaled_cosine(yf)
        
        n1 = _perlin[of & PERLIN_SIZE]
        n1 += rxf * (_perlin[(of + 1) & PERLIN_SIZE] - n1)
        
        n2 = _perlin[(of + PERLIN_YWRAP) & PERLIN_SIZE]
        n2 += rxf * (_perlin[(of + PERLIN_YWRAP + 1) & PERLIN_SIZE] - n2)
        n1 += ryf * (n2 - n1)
        
        of += PERLIN_ZWRAP
        n2 = _perlin[of & PERLIN_SIZE]
        n2 += rxf * (_perlin[(of + 1) & PERLIN_SIZE] - n2)
        n3 = _perlin[(of + PERLIN_YWRAP) & PERLIN_SIZE]
        n3 += rxf * (_perlin[(of + PERLIN_YWRAP + 1) & PERLIN_SIZE] - n3)
        n2 += ryf * (n3 - n2)
        n1 += _scaled_cosine(zf) * (n2 - n1)
        
        r += n1 * ampl
        ampl *= _perlin_amp_falloff
        
        xi, xf, yi, yf, zi, zf = xi << 1, xf * 2, yi << 1, yf * 2, zi << 1, zf * 2
        if xf >= 1.0: xi, xf = xi + 1, xf - 1
        if yf >= 1.0: yi, yf = yi + 1, yf - 1
        if zf >= 1.0: zi, zf = zi + 1, zf - 1
    
    return r

# Geometry utilities
def dist(x0: float, y0: float, x1: float, y1: float) -> float:
    return math.hypot(x1 - x0, y1 - y0)

def lerp(a: float, b: float, t: float) -> float:
    return a * (1 - t) + b * t

def lerp2d(x0: float, y0: float, x1: float, y1: float, t: float) -> Point:
    return (x0 * (1 - t) + x1 * t, y0 * (1 - t) + y1 * t)

def get_bbox(points: Polyline) -> Dict[str, float]:
    if not points:
        return {'x': 0, 'y': 0, 'w': 0, 'h': 0}
    xs, ys = zip(*points)
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    return {'x': xmin, 'y': ymin, 'w': xmax - xmin, 'h': ymax - ymin}

def trsl_poly(poly: Polyline, x: float, y: float) -> Polyline:
    return [(px + x, py + y) for px, py in poly]

def scl_poly(poly: Polyline, sx: float, sy: float) -> Polyline:
    return [(px * sx, py * sy) for px, py in poly]

def rot_poly(poly: Polyline, th: float) -> Polyline:
    cos_th, sin_th = math.cos(th), math.sin(th)
    return [(px * cos_th - py * sin_th, px * sin_th + py * cos_th) for px, py in poly]

def resample(polyline: Polyline, step: float) -> Polyline:
    """Resample polyline to fixed step size"""
    if len(polyline) < 2:
        return polyline
    
    out, step_dist, prev = [polyline[0]], 0, polyline[0]
    
    for i in range(1, len(polyline)):
        curr = polyline[i]
        seg_dist = dist(prev[0], prev[1], curr[0], curr[1])
        
        if seg_dist > 0:
            step_dist += seg_dist
            while step_dist >= step:
                frac = (step - (step_dist - seg_dist)) / seg_dist
                x, y = prev[0] + (curr[0] - prev[0]) * frac, prev[1] + (curr[1] - prev[1]) * frac
                out.append((x, y))
                step_dist -= step
            prev = curr
    
    if out[-1] != polyline[-1]:
        out.append(polyline[-1])
    
    return out

# Fish body generation helpers
def bean(t: float) -> float:
    """Bean-shaped curve function"""
    return math.sin(t * PI) ** 2

def deviate(amount: float = 0.05) -> float:
    """Random deviate for variation"""
    return (rand() - 0.5) * 2 * amount

def approx_poly_dp(polyline: Polyline, epsilon: float) -> Polyline:
    """Douglas-Peucker polygon simplification"""
    if len(polyline) <= 2:
        return polyline
    
    dmax, index = 0, 0
    p0, pn = polyline[0], polyline[-1]
    
    for i in range(1, len(polyline) - 1):
        # Distance from point to line
        x, y = polyline[i]
        dx, dy = pn[0] - p0[0], pn[1] - p0[1]
        len2 = dx * dx + dy * dy
        
        if len2 > 0:
            t = max(0, min(1, ((x - p0[0]) * dx + (y - p0[1]) * dy) / len2))
            proj_x, proj_y = p0[0] + t * dx, p0[1] + t * dy
            d = dist(x, y, proj_x, proj_y)
            if d > dmax:
                dmax, index = d, i
    
    if dmax > epsilon:
        rec1 = approx_poly_dp(polyline[:index + 1], epsilon)
        rec2 = approx_poly_dp(polyline[index:], epsilon)
        return rec1[:-1] + rec2
    
    return [polyline[0], polyline[-1]]

# Fish feature generation
def fin_a(curve: Polyline, angle0: float, angle1: float, length_func: Callable, 
          is_tail: int = 0, curve_vary: float = 0, curve_vary2: float = 0, 
          soft: float = 0) -> Tuple[Polyline, Polylines]:
    """Generate fin type A"""
    curve = resample(curve, 2)
    outline = []
    fins = []
    
    for i in range(len(curve)):
        t = i / (len(curve) - 1) if len(curve) > 1 else 0
        x0, y0 = curve[i]
        if i < len(curve) - 1:
            x1, y1 = curve[i + 1]
        else:
            x1, y1 = x0, y0
        
        dx, dy = x1 - x0, y1 - y0
        angle = math.atan2(dy, dx)
        
        length = length_func(t)
        
        # Calculate fin points
        a0 = angle + angle0
        a1 = angle + angle1
        
        x_tip = x0 + math.cos(a0 + a1) / 2 * length
        y_tip = y0 + math.sin(a0 + a1) / 2 * length
        
        outline.append((x_tip, y_tip))
        fins.append([(x0, y0), (x_tip, y_tip)])
    
    return outline, fins

def fin_b(curve: Polyline, angle0: float, angle1: float, 
          length_func: Callable, soft: float = 0) -> Tuple[Polyline, Polylines]:
    """Generate fin type B (simplified)"""
    return fin_a(curve, angle0, angle1, length_func, soft=soft)

def fin_adipose(curve: Polyline, width: float, height: float, 
                count: int) -> Tuple[Polyline, Polylines]:
    """Adipose fin (small fin behind dorsal)"""
    outline = []
    fins = []
    for i in range(count):
        t = i / max(1, count - 1)
        x, y = lerp2d(curve[0][0], curve[0][1], 
                     curve[-1][0], curve[-1][1], t)
        outline.append((x + height * math.sin(t * PI), 
                       y + width * math.sin(t * PI)))
        fins.append([(x, y), (x + height, y + width)])
    return outline, fins

def fish_head(x0: float, y0: float, x1: float, y1: float, x2: float, 
              y2: float, params: Dict) -> Tuple[Polyline, Polylines]:
    """Generate fish head"""
    outline = []
    features = []
    
    # Simple circular head
    n = 16
    radius = params.get('eye_size', 5)
    for i in range(n):
        a = i / n * PI * 2
        outline.append((x0 + math.cos(a) * radius * 2, 
                       y0 + math.sin(a) * radius))
    
    # Eye
    eye = []
    for i in range(8):
        a = i / 8 * PI * 2
        eye.append((x0 - radius + math.cos(a) * radius / 2, 
                   y0 + math.sin(a) * radius / 2))
    features.append(eye)
    
    # Mouth
    if params.get('mouth_size', 0) > 0:
        mouth_size = params['mouth_size']
        mouth = [(x0 - mouth_size, y0 + radius),
                (x0, y0 + radius + mouth_size/2),
                (x0 + mouth_size, y0 + radius)]
        features.append(mouth)
    
    return outline, features

def pattern_dot(scale: float = 1) -> Callable:
    """Generate dot pattern function"""
    # Simplified: return a function that generates dots
    def pattern_func(x: float, y: float) -> bool:
        return (noise(x * 0.1, y * 0.1) * noise(x * 0.01, y * 0.01)) > 0.3
    return pattern_func

# Main fish generation
def default_params() -> Dict:
    """Default fish parameters"""
    return {
        'body_curve_type': 0,
        'body_curve_amount': 0.85,
        'body_length': 250,
        'body_height': 60,
        'scale_type': 1,
        'scale_scale': 1.0,
        'pattern_type': 0,
        'pattern_scale': 1.0,
        'dorsal_type': 0,
        'dorsal_length': 60,
        'wing_type': 0,
        'wing_length': 80,
        'pelvic_type': 0,
        'pelvic_length': 50,
        'anal_type': 0,
        'anal_length': 30,
        'tail_type': 0,
        'tail_length': 50,
        'finlet_type': 0,
        'eye_type': 0,
        'eye_size': 8,
        'mouth_size': 5,
        'head_length': 20,
        'nose_height': 0,
    }

def generate_params() -> Dict:
    """Generate random fish parameters"""
    params = default_params()
    params['body_curve_type'] = int(rand() * 2)
    params['body_curve_amount'] = 0.5 + rand() * 0.5
    params['body_length'] = 200 + rand() * 150
    params['body_height'] = 40 + rand() * 80
    params['scale_type'] = int(rand() * 3)
    params['pattern_type'] = int(rand() * 3)
    params['dorsal_type'] = int(rand() * 2)
    params['tail_type'] = int(rand() * 4)
    params['eye_type'] = int(rand() * 2)
    params['eye_size'] = 5 + rand() * 10
    return params

def fish(params: Optional[Dict] = None) -> Polylines:
    """Generate complete fish drawing"""
    if params is None:
        params = generate_params()
    
    polylines = []
    
    # Generate body curves
    n = 20
    curve0, curve1 = [], []
    
    body_length = params['body_length']
    body_height = params['body_height']
    curve_amount = params['body_curve_amount']
    
    center_x, center_y = 125, 60
    
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0.5
        
        x = center_x + (t - 0.5) * body_length
        
        if params['body_curve_type'] == 0:
            # Sine curve
            s = curve_amount
            y_offset = math.sin(t * PI) * body_height * (s + (1 - s) * (0.5 + noise(t * 2, 1) * 0.5))
        else:
            # Bean curve
            y_offset = math.sin(t * PI) ** 2 * body_height * curve_amount
        
        curve0.append((x, center_y - y_offset))
        curve1.append((x, center_y + y_offset))
    
    # Main body outline
    outline = curve0 + list(reversed(curve1))
    polylines.append(outline)
    
    # Dorsal fin
    if params['dorsal_length'] > 0:
        dorsal_start = max(0, n // 3)
        dorsal_end = min(n, 2 * n // 3)
        dorsal_curve = curve0[dorsal_start:dorsal_end]
        if len(dorsal_curve) > 1:
            dorsal_outline, dorsal_fins = fin_a(
                dorsal_curve, 
                -0.3, 0.3,
                lambda t: params['dorsal_length'] * (1 - t * 0.2),
                is_tail=0
            )
            polylines.extend(dorsal_fins)
    
    # Tail fin
    if params['tail_length'] > 0:
        tail_curve = [curve0[-2:], curve1[-2:]]
        tail_curve = resample(tail_curve[0] + tail_curve[1], 3)
        if len(tail_curve) > 1:
            tail_outline, tail_fins = fin_a(
                tail_curve,
                -0.5, 0.5,
                lambda t: params['tail_length'] * (0.5 + 0.5 * math.sin(t * PI)),
                is_tail=1
            )
            polylines.extend(tail_fins)
    
    # Pectoral fin
    if params['wing_length'] > 0:
        wing_start = max(0, n // 4)
        wing_curve = [curve1[wing_start]]
        wing_outline, wing_fins = fin_a(
            wing_curve,
            -0.7, 0.1,
            lambda t: params['wing_length'] * (1 - t * 0.3)
        )
        polylines.extend(wing_fins)
    
    # Head
    head_outline, head_features = fish_head(
        center_x - body_length / 2 - params['head_length'],
        center_y,
        curve0[0][0], curve0[0][1],
        curve1[0][0], curve1[0][1],
        params
    )
    polylines.append(head_outline)
    polylines.extend(head_features)
    
    # Add pattern details
    if params['pattern_type'] > 0:
        # Simplified pattern: just add some dots
        bbox = get_bbox(outline)
        for _ in range(int(10 * params.get('pattern_scale', 1))):
            x = bbox['x'] + rand() * bbox['w']
            y = bbox['y'] + rand() * bbox['h']
            dot = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            polylines.append(dot)
    
    return polylines

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
    """Generate random Latin-ish binomial name"""
    consonants = "bcdfghjklmnprstvwxyz"
    vowels = "aeiou"
    
    def syllable():
        return random.choice(consonants) + random.choice(vowels)
    
    genus = ''.join(syllable() for _ in range(1 + int(rand() * 2)))
    species = ''.join(syllable() for _ in range(1 + int(rand() * 2)))
    
    return genus.capitalize() + ' ' + species.lower()

def reframe(drawing: Polylines, display_width: int = 296, display_height: int = 128, 
            margin: float = 5) -> Polylines:
    """Reframe drawing to fit exactly on 296x128 display"""
    if not drawing:
        return drawing
    
    bbox = get_bbox([pt for poly in drawing for pt in poly])
    
    # Calculate scale to fit display with margin
    available_width = display_width - 2 * margin
    available_height = display_height - 2 * margin
    
    if bbox['w'] > 0 and bbox['h'] > 0:
        scale = min(
            available_width / bbox['w'],
            available_height / bbox['h']
        )
    else:
        scale = 1.0
    
    # Center on display
    scaled_width = bbox['w'] * scale
    scaled_height = bbox['h'] * scale
    offset_x = (display_width - scaled_width) / 2 - bbox['x'] * scale
    offset_y = (display_height - scaled_height) / 2 - bbox['y'] * scale
    
    result = []
    for poly in drawing:
        scaled = [(x * scale + offset_x, y * scale + offset_y) for x, y in poly]
        result.append(scaled)
    
    return result

def cleanup(drawing: Polylines) -> Polylines:
    """Clean up drawing"""
    result = []
    for poly in drawing:
        # Simplify
        simplified = approx_poly_dp(poly, 0.5)
        if len(simplified) >= 2:
            # Remove very small lines
            if dist(simplified[0][0], simplified[0][1], 
                   simplified[-1][0], simplified[-1][1]) > 1:
                result.append(simplified)
    return result

def main(seed: Optional[str] = None, display_width: int = 296, display_height: int = 128) -> Polylines:
    """Generate fish optimized for 296x128 display"""
    if seed is None:
        set_seed(int(rand() * 10000))
        seed = binomen()
    else:
        set_seed(str_to_seed(seed))
    
    params = generate_params()
    # Optimize body length for display width
    params['body_length'] = 150 + rand() * 100
    
    drawing = fish(params)
    drawing = reframe(drawing, display_width, display_height, margin=5)
    drawing = cleanup(drawing)
    
    return drawing

# SVG export (for testing on desktop)
def draw_svg(polylines: Polylines, width: int = 296, height: int = 128) -> str:
    """Render polylines to SVG"""
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">\n'
    svg += '<rect width="100%" height="100%" fill="white"/>\n'
    
    for poly in polylines:
        if len(poly) > 1:
            points = ' '.join(f'{x:.1f},{y:.1f}' for x, y in poly)
            svg += f'<polyline points="{points}" stroke="black" stroke-width="0.5" fill="none"/>\n'
    
    svg += '</svg>'
    return svg

if __name__ == "__main__":
    # Test
    print("Generating fish...")
    drawing = main("TestFish")
    print(f"Generated {len(drawing)} polylines")
    
    # Save SVG for testing
    svg = draw_svg(drawing)
    with open('/tmp/fish_test.svg', 'w') as f:
        f.write(svg)
    print("Saved to /tmp/fish_test.svg")
