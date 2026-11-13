"""
FishDraw for Badger2040
Display driver and integration for Pimoroni Badger2040 e-ink display
"""

import gc
from fishdraw_complete import main, draw_svg

class BadgerFish:
    """FishDraw controller for Badger2040"""
    
    DISPLAY_WIDTH = 296
    DISPLAY_HEIGHT = 128
    
    def __init__(self):
        """Initialize Badger2040 display"""
        try:
            import badger2040
            self.badger = badger2040.Badger2040()
            self.has_display = True
        except ImportError:
            print("Badger2040 library not found - running in simulation mode")
            self.badger = None
            self.has_display = False
    
    def draw_polylines(self, polylines, thickness=1):
        """Draw polylines on the display"""
        if not self.has_display:
            print("Display simulation: Would draw", len(polylines), "polylines")
            return
        
        # Clear display
        self.badger.clear()
        
        # Draw each polyline
        for polyline in polylines:
            if len(polyline) < 2:
                continue
            
            # Draw line segments
            for i in range(len(polyline) - 1):
                x0, y0 = int(polyline[i][0]), int(polyline[i][1])
                x1, y1 = int(polyline[i + 1][0]), int(polyline[i + 1][1])
                
                # Bresenham line drawing
                self._draw_line(x0, y0, x1, y1, thickness)
        
        # Update display
        self.badger.update()
    
    def _draw_line(self, x0, y0, x1, y1, thickness=1):
        """Draw line using Bresenham algorithm"""
        if not self.has_display:
            return
        
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            # Draw pixel with thickness
            for tx in range(-thickness//2, thickness//2 + 1):
                for ty in range(-thickness//2, thickness//2 + 1):
                    px, py = x0 + tx, y0 + ty
                    if 0 <= px < self.DISPLAY_WIDTH and 0 <= py < self.DISPLAY_HEIGHT:
                        self.badger.pixel(px, py, 1)
            
            if x0 == x1 and y0 == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
    
    def generate_and_display(self, seed=None):
        """Generate a fish and display it as a finished drawing"""
        print("Generating fish...")
        drawing = main(seed, self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)
        print(f"Generated {len(drawing)} polylines")
        
        print("Drawing to display...")
        self.draw_polylines(drawing, thickness=1)
        print("Done!")
        
        # Free memory
        gc.collect()
    
    def demo_mode(self):
        """Run demo mode with different fish"""
        seeds = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
        for seed in seeds:
            print(f"\n=== Generating {seed} ===")
            self.generate_and_display(seed)
            
            if self.has_display:
                # Wait for user interaction (on real Badger2040)
                try:
                    # This is specific to Badger2040 buttons
                    import time
                    time.sleep(3)
                except:
                    pass


def main_badger():
    """Main entry point for Badger2040"""
    print("FishDraw for Badger2040")
    print("=" * 30)
    
    badger_fish = BadgerFish()
    
    if badger_fish.has_display:
        print("Badger2040 detected!")
        # In real usage, you'd add button handling here
        badger_fish.generate_and_display()
    else:
        print("Running in simulation mode")
        badger_fish.demo_mode()


if __name__ == "__main__":
    main_badger()

