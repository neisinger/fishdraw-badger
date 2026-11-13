"""
FishDraw for Badger2040 - Standalone version
Optimized for memory constraints on MicroPython
"""

import json
import random
import time
import math

# ============================================================================
# SIMPLIFIED FISH GENERATION
# ============================================================================

class SeededRandom:
    """Deterministic random number generator"""
    def __init__(self, seed=None):
        if seed is None:
            self.jsr = 0x5EED
        else:
            if isinstance(seed, str):
                self.jsr = hash(seed) & 0xFFFFFFFF
            else:
                self.jsr = int(seed) & 0xFFFFFFFF
    
    def rand(self):
        self.jsr ^= (self.jsr << 17) & 0xFFFFFFFF
        self.jsr ^= (self.jsr >> 13) & 0xFFFFFFFF
        self.jsr ^= (self.jsr << 5) & 0xFFFFFFFF
        return ((self.jsr >> 0) & 0xFFFFFFFF) / 4294967295.0


class SimpleNoise:
    """Simple noise generator for MicroPython"""
    def __init__(self, rand_gen):
        self.rand_gen = rand_gen
    
    def noise(self, x, seed=0):
        # Hash-based noise (memory efficient)
        xi = int(x * 10) & 0xFFFFFF
        t = (xi * 73856093) ^ (int(seed) * 19349663)
        t = (t * 12345 + 67890) & 0xFFFFFFFF
        return (t / 4294967295.0) * 2.0 - 1.0


def generate_fish(seed=None, width=296, height=128):
    """Generate a fish and return polylines"""
    if seed is None:
        seed = int(random.random() * 1000000)
    
    rand_gen = SeededRandom(seed)
    noise_gen = SimpleNoise(rand_gen)
    
    polylines = []
    
    # Generate body parameters
    body_len = 80 + rand_gen.rand() * 50
    body_height = 25 + rand_gen.rand() * 25
    body_waves = 2 + rand_gen.rand() * 2
    head_x = 30
    
    # Main body - wavy line
    body = []
    segments = int(body_len / 4)
    for i in range(segments):
        t = i / max(segments - 1, 1)
        x = head_x + t * body_len
        # Wave pattern
        wave = math.sin(t * body_waves * math.pi) * body_height * 0.4
        n = noise_gen.noise(t * 3, seed)
        noise = n * body_height * 0.2
        y = 64 + wave + noise
        body.append([x, y])
    
    if body:
        polylines.append(body)
    
    # Eyes (simple circles)
    if len(body) > 0:
        eye_x = body[0][0] + 5
        eye_y = body[0][1]
        
        for eye_offset in [-6, 6]:
            eye = []
            eye_size = 2 + rand_gen.rand() * 1.5
            for i in range(9):
                angle = (i / 8) * math.pi * 2
                ex = eye_x + math.cos(angle) * eye_size
                ey = eye_y + eye_offset + math.sin(angle) * eye_size * 0.7
                eye.append([ex, ey])
            if eye:
                polylines.append(eye)
    
    # Dorsal fin
    if len(body) > 2:
        mid = len(body) // 2
        fin_base_x = body[mid][0]
        fin_base_y = body[mid][1]
        fin_height = body_height * (0.5 + rand_gen.rand() * 0.4)
        
        fin = []
        for i in range(3):
            t = i / 2
            fx = fin_base_x + t * 12
            fy = fin_base_y - fin_height * (1 - abs(t - 0.5) * 2)
            fin.append([fx, fy])
        if fin:
            polylines.append(fin)
    
    # Tail
    if len(body) > 0:
        tail_x = body[-1][0]
        tail_y = body[-1][1]
        tail_size = body_height * (0.6 + rand_gen.rand() * 0.4)
        
        tail = []
        for i in range(9):
            angle = (i / 8) * math.pi * 2
            tx = tail_x + 15 + math.cos(angle) * tail_size
            ty = tail_y + math.sin(angle) * tail_size * 0.6
            tail.append([tx, ty])
        if tail:
            polylines.append(tail)
    
    # Center and scale to display
    if polylines:
        xmin, ymin = float('inf'), float('inf')
        xmax, ymax = float('-inf'), float('-inf')
        
        for poly in polylines:
            for pt in poly:
                xmin = min(xmin, pt[0])
                ymin = min(ymin, pt[1])
                xmax = max(xmax, pt[0])
                ymax = max(ymax, pt[1])
        
        if xmin != float('inf'):
            w = xmax - xmin
            h = ymax - ymin
            padding = 10
            
            scale_x = (width - padding * 2) / max(w, 1)
            scale_y = (height - padding * 2) / max(h, 1)
            scale = min(scale_x, scale_y, 1.0)
            
            cx = (xmin + xmax) / 2
            cy = (ymin + ymax) / 2
            center_x = width / 2
            center_y = height / 2
            
            for poly in polylines:
                for pt in poly:
                    pt[0] = center_x + (pt[0] - cx) * scale
                    pt[1] = center_y + (pt[1] - cy) * scale
    
    return polylines


def generate_name():
    """Generate a random fish name"""
    vowels = "aeiou"
    consonants = "bcdfghjklmnprstvwxyz"
    
    def syllable():
        return random.choice(consonants) + random.choice(vowels)
    
    genus = syllable().capitalize() + random.choice(consonants) + random.choice(vowels)
    species = syllable() + random.choice(consonants)
    
    return f"{genus} {species}"


# ============================================================================
# BADGER2040 DISPLAY DRIVER
# ============================================================================

class BadgerFish:
    """FishDraw controller for Badger2040"""
    
    def __init__(self, config_path="config.json"):
        self.load_config(config_path)
        
        self.badger = None
        self.has_display = False
        self.button_a = None
        self.button_b = None
        self.button_c = None
        self.button_up = None
        self.button_down = None
        
        try:
            import badger2040
            self.badger = badger2040.Badger2040()
            self.button_a = badger2040.BUTTON_A
            self.button_b = badger2040.BUTTON_B
            self.button_c = badger2040.BUTTON_C
            self.button_up = badger2040.BUTTON_UP
            self.button_down = badger2040.BUTTON_DOWN
            self.has_display = True
            print("✓ Badger2040 display initialized")
        except Exception as e:
            print(f"Display not available: {e}")
        
        self.history = []
        self.current_history_index = -1
        self.current_seed = None
        self.current_name = None
        self.current_drawing = None
        self.last_button_time = 0
    
    def load_config(self, path="config.json"):
        try:
            with open(path, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {
                "seed_step": 10,
                "history_size": 200,
                "button_delay_ms": 200,
                "display_width": 296,
                "display_height": 128
            }
        
        self.DISPLAY_WIDTH = self.config.get("display_width", 296)
        self.DISPLAY_HEIGHT = self.config.get("display_height", 128)
        self.SEED_STEP = self.config.get("seed_step", 10)
        self.HISTORY_SIZE = self.config.get("history_size", 200)
        self.BUTTON_DELAY = self.config.get("button_delay_ms", 200) / 1000.0
    
    def draw_polylines(self, polylines):
        if not self.has_display:
            print(f"Sim: {len(polylines)} polylines")
            return
        
        self.badger.clear()
        
        for polyline in polylines:
            if len(polyline) < 2:
                continue
            
            for i in range(len(polyline) - 1):
                x0 = int(polyline[i][0])
                y0 = int(polyline[i][1])
                x1 = int(polyline[i + 1][0])
                y1 = int(polyline[i + 1][1])
                
                self.badger.line(x0, y0, x1, y1, 1, 1)
        
        self.badger.update()
    
    def generate_and_display(self, seed=None):
        if seed is None:
            seed = int(random.random() * 1000000)
        
        print(f"Generating: {seed}...")
        polylines = generate_fish(seed, self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)
        print(f"Polylines: {len(polylines)}")
        
        self.draw_polylines(polylines)
        
        self.current_seed = seed
        self.current_drawing = polylines
        self.current_name = generate_name()
        
        if seed not in self.history:
            self.history.append(seed)
            if len(self.history) > self.HISTORY_SIZE:
                self.history.pop(0)
        
        self.current_history_index = self.history.index(seed)
        print(f"Name: {self.current_name}")
    
    def button_a_pressed(self):
        if self.current_seed is not None:
            self.generate_and_display(self.current_seed - self.SEED_STEP)
    
    def button_b_pressed(self):
        self.generate_and_display()
    
    def button_c_pressed(self):
        if self.current_seed is not None:
            self.generate_and_display(self.current_seed + self.SEED_STEP)
    
    def button_up_pressed(self):
        if self.history and self.current_history_index > 0:
            self.current_history_index -= 1
            self.generate_and_display(self.history[self.current_history_index])
    
    def button_down_pressed(self):
        if self.history and self.current_history_index < len(self.history) - 1:
            self.current_history_index += 1
            self.generate_and_display(self.history[self.current_history_index])
    
    def run(self):
        print("\nFishDraw for Badger2040\n")
        
        if not self.has_display:
            print("Simulation mode")
            self.generate_and_display()
            return
        
        self.generate_and_display()
        
        while True:
            now = time.time()
            
            if now - self.last_button_time < self.BUTTON_DELAY:
                time.sleep(0.01)
                continue
            
            if self.badger.pressed(self.button_a):
                self.button_a_pressed()
                self.last_button_time = now
            elif self.badger.pressed(self.button_b):
                self.button_b_pressed()
                self.last_button_time = now
            elif self.badger.pressed(self.button_c):
                self.button_c_pressed()
                self.last_button_time = now
            elif self.badger.pressed(self.button_up):
                self.button_up_pressed()
                self.last_button_time = now
            elif self.badger.pressed(self.button_down):
                self.button_down_pressed()
                self.last_button_time = now
            
            time.sleep(0.01)


if __name__ == "__main__":
    fish = BadgerFish()
    fish.run()
