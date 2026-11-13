"""
FishDraw - Procedurally generated fish drawings
Python port optimized for MicroPython/Badger2040
Based on https://github.com/LingDong-/fishdraw by LingDong
"""

import math
import random

# Random number generator (seeded)
class SeededRandom:
    def __init__(self, seed=None):
        if seed is None:
            self.jsr = 0x5EED
        else:
            # Convert string seed to integer
            if isinstance(seed, str):
                self.jsr = hash(seed) & 0xFFFFFFFF
            else:
                self.jsr = seed & 0xFFFFFFFF
    
    def rand(self):
        self.jsr ^= (self.jsr << 17) & 0xFFFFFFFF
        self.jsr ^= (self.jsr >> 13) & 0xFFFFFFFF
        self.jsr ^= (self.jsr << 5) & 0xFFFFFFFF
        return ((self.jsr >> 0) & 0xFFFFFFFF) / 4294967295.0


# Perlin noise
class PerlinNoise:
    def __init__(self, rand_gen):
        self.PERLIN_YWRAPB = 4
        self.PERLIN_YWRAP = 1 << self.PERLIN_YWRAPB
        self.PERLIN_ZWRAPB = 8
        self.PERLIN_ZWRAP = 1 << self.PERLIN_ZWRAPB
        self.PERLIN_SIZE = 4095
        self.perlin_octaves = 4
        self.perlin_amp_falloff = 0.5
        self.perlin = None
        self.rand_gen = rand_gen
    
    def scaled_cosine(self, i):
        return 0.5 * (1.0 - math.cos(i * math.pi))
    
    def noise(self, x, y=0, z=0):
        if self.perlin is None:
            self.perlin = [self.rand_gen.rand() for _ in range(self.PERLIN_SIZE + 1)]
        
        if x < 0:
            x = -x
        if y < 0:
            y = -y
        if z < 0:
            z = -z
        
        xi = int(x)
        yi = int(y)
        zi = int(z)
        xf = x - xi
        yf = y - yi
        zf = z - zi
        
        r = 0.0
        ampl = 0.5
        
        for o in range(self.perlin_octaves):
            of = xi + (yi << self.PERLIN_YWRAPB) + (zi << self.PERLIN_ZWRAPB)
            rxf = self.scaled_cosine(xf)
            ryf = self.scaled_cosine(yf)
            
            n1 = self.perlin[of & self.PERLIN_SIZE]
            n1 += rxf * (self.perlin[(of + 1) & self.PERLIN_SIZE] - n1)
            n2 = self.perlin[(of + self.PERLIN_YWRAP) & self.PERLIN_SIZE]
            n2 += rxf * (self.perlin[(of + self.PERLIN_YWRAP + 1) & self.PERLIN_SIZE] - n2)
            n1 += ryf * (n2 - n1)
            
            of += self.PERLIN_ZWRAP
            n2 = self.perlin[of & self.PERLIN_SIZE]
            n2 += rxf * (self.perlin[(of + 1) & self.PERLIN_SIZE] - n2)
            n3 = self.perlin[(of + self.PERLIN_YWRAP) & self.PERLIN_SIZE]
            n3 += rxf * (self.perlin[(of + self.PERLIN_YWRAP + 1) & self.PERLIN_SIZE] - n3)
            n2 += ryf * (n3 - n2)
            n1 += self.scaled_cosine(zf) * (n2 - n1)
            r += n1 * ampl
            ampl *= self.perlin_amp_falloff
            
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


class FishDraw:
    def __init__(self, seed=None, width=296, height=128):
        self.seed = seed
        self.width = width
        self.height = height
        self.rand_gen = SeededRandom(seed)
        self.perlin = PerlinNoise(self.rand_gen)
        self.polylines = []
    
    def rand(self):
        return self.rand_gen.rand()
    
    def noise(self, x, y=0, z=0):
        return self.perlin.noise(x, y, z)
    
    def generate(self):
        """Generate a fish and return polylines"""
        self.polylines = []
        
        # Generate fish parameters
        body_len = 120 + self.rand() * 60
        body_height = 30 + self.rand() * 30
        body_wave = 2 + self.rand() * 3
        
        # Body
        body = self._generate_body(body_len, body_height, body_wave)
        self.polylines.append(body)
        
        # Head details
        for _ in range(2):
            eye = self._generate_eye(body[0][0], body[0][1])
            if eye:
                self.polylines.append(eye)
        
        # Fins
        fins = self._generate_fins(body, body_height)
        self.polylines.extend(fins)
        
        # Tail
        tail = self._generate_tail(body[-1], body_height)
        if tail:
            self.polylines.append(tail)
        
        # Center and scale to display
        self._center_and_scale()
        
        return self.polylines
    
    def _generate_body(self, length, height, wave_count):
        """Generate main body curve"""
        points = []
        segments = int(length / 5)
        
        for i in range(segments):
            t = i / max(segments - 1, 1)
            x = 50 + t * length
            # Wave pattern
            wave = math.sin(t * wave_count * math.pi) * height * 0.5
            y = 64 + wave + (self.noise(t * 3, 0) - 0.5) * height
            points.append([x, y])
        
        return points
    
    def _generate_eye(self, x, y):
        """Generate eye"""
        eye_x = x + 10
        eye_y = y - 8
        eye_size = 3 + self.rand() * 2
        
        points = []
        segments = 8
        for i in range(segments + 1):
            angle = (i / segments) * math.pi * 2
            px = eye_x + math.cos(angle) * eye_size
            py = eye_y + math.sin(angle) * eye_size
            points.append([px, py])
        
        return points if len(points) > 2 else None
    
    def _generate_fins(self, body, body_height):
        """Generate dorsal and ventral fins"""
        fins = []
        
        # Dorsal fin
        if len(body) > 2:
            mid_idx = len(body) // 2
            base_x = body[mid_idx][0]
            base_y = body[mid_idx][1]
            
            fin_height = body_height * (0.6 + self.rand() * 0.4)
            fin_length = 15 + self.rand() * 10
            
            fin = []
            for i in range(3):
                t = i / 2
                x = base_x + t * fin_length
                y = base_y - fin_height * (1 - abs(t - 0.5) * 2)
                fin.append([x, y])
            
            fins.append(fin)
        
        return fins
    
    def _generate_tail(self, tail_pos, body_height):
        """Generate tail fin"""
        x0, y0 = tail_pos
        tail_size = body_height * (0.7 + self.rand() * 0.5)
        
        tail = []
        segments = 8
        for i in range(segments + 1):
            angle = (i / segments) * math.pi * 2
            x = x0 + 20 + math.cos(angle) * tail_size
            y = y0 + math.sin(angle) * tail_size * 0.7
            tail.append([x, y])
        
        return tail if len(tail) > 2 else None
    
    def _center_and_scale(self):
        """Center and scale polylines to fit display"""
        if not self.polylines:
            return
        
        # Find bounds
        xmin, ymin = float('inf'), float('inf')
        xmax, ymax = float('-inf'), float('-inf')
        
        for poly in self.polylines:
            for point in poly:
                xmin = min(xmin, point[0])
                ymin = min(ymin, point[1])
                xmax = max(xmax, point[0])
                ymax = max(ymax, point[1])
        
        if xmin == float('inf'):
            return
        
        # Calculate scale
        w = xmax - xmin
        h = ymax - ymin
        
        padding = 10
        scale_x = (self.width - padding * 2) / max(w, 1)
        scale_y = (self.height - padding * 2) / max(h, 1)
        scale = min(scale_x, scale_y, 1.0)
        
        # Center
        cx = (xmin + xmax) / 2
        cy = (ymin + ymax) / 2
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Transform
        for poly in self.polylines:
            for point in poly:
                point[0] = center_x + (point[0] - cx) * scale
                point[1] = center_y + (point[1] - cy) * scale


def generate_fish(seed=None, width=296, height=128):
    """Generate a fish drawing and return polylines"""
    fish = FishDraw(seed, width, height)
    return fish.generate()


def generate_name():
    """Generate a random pseudo-Latin fish name"""
    vowels = "aeiou"
    consonants = "bcdfghjklmnprstvwxyz"
    
    def syllable():
        return random.choice(consonants) + random.choice(vowels)
    
    # Generate binomen (2-part name)
    genus = syllable().capitalize() + random.choice(consonants) + random.choice(vowels)
    species = syllable() + random.choice(consonants)
    
    return f"{genus} {species}"
