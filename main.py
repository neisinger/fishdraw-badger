"""
FishDraw for Badger2040 - Main entry point
This file should be placed as /main.py on the Badger2040

Button mappings (Badger2040):
  A      = Generate new fish
  B      = Change fish style
  C      = Show info
  UP     = Adjust parameter (scale up)
  DOWN   = Adjust parameter (scale down)
"""

import gc
import time
try:
    import badger2040
    BADGER_AVAILABLE = True
except ImportError:
    BADGER_AVAILABLE = False
    print("Running in simulation mode")

from fishdraw_complete import main as generate_fish, draw_svg


class FishDrawApp:
    """Main application for Badger2040"""
    
    def __init__(self):
        if BADGER_AVAILABLE:
            self.badger = badger2040.Badger2040()
            self.width = 296
            self.height = 128
        else:
            self.badger = None
            self.width = 296
            self.height = 128
        
        self.current_fish = None
        self.current_seed = None
        self.fish_count = 0
        self.style = 0  # 0=normal, 1=aggressive, 2=elegant
        self.scale = 1.0
    
    def clear_display(self):
        """Clear the display"""
        if not self.badger:
            print("Cleared (simulated)")
            return
        
        self.badger.clear()
    
    def draw_text(self, x, y, text, scale=1):
        """Draw text on display"""
        if not self.badger:
            print(f"Text at ({x},{y}): {text}")
            return
        
        # Simple text drawing - using badger's text function if available
        try:
            self.badger.text(text, x, y, scale=scale)
        except:
            # Fallback - just print
            print(text)
    
    def draw_polylines(self, polylines):
        """Draw fish polylines on display"""
        if not self.badger:
            print(f"Drawing {len(polylines)} polylines (simulated)")
            return
        
        for polyline in polylines:
            if len(polyline) < 2:
                continue
            
            # Draw each line segment
            for i in range(len(polyline) - 1):
                x0 = int(polyline[i][0])
                y0 = int(polyline[i][1])
                x1 = int(polyline[i + 1][0])
                y1 = int(polyline[i + 1][1])
                
                # Clip to display bounds
                if (0 <= x0 < self.width and 0 <= y0 < self.height and
                    0 <= x1 < self.width and 0 <= y1 < self.height):
                    self._draw_line(x0, y0, x1, y1)
    
    def _draw_line(self, x0, y0, x1, y1):
        """Draw line using Bresenham algorithm"""
        if not self.badger:
            return
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            if 0 <= x0 < self.width and 0 <= y0 < self.height:
                self.badger.pixel(x0, y0, 1)
            
            if x0 == x1 and y0 == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
    
    def update_display(self):
        """Update the e-ink display"""
        if self.badger:
            try:
                self.badger.update()
            except Exception as e:
                print(f"Display update error: {e}")
    
    def generate_new_fish(self, seed=None):
        """Generate a new fish and display it"""
        print(f"Generating fish #{self.fish_count}...")
        
        try:
            # Clear display
            self.clear_display()
            
            # Show status
            self.draw_text(10, 10, "Generating...", scale=1)
            self.update_display()
            
            # Generate fish
            print("  Calling fishdraw.main()...")
            self.current_fish = generate_fish(seed)
            self.current_seed = seed
            
            print(f"  Generated {len(self.current_fish)} polylines")
            
            # Clear for drawing
            self.clear_display()
            
            # Draw the fish
            print("  Drawing to display...")
            self.draw_polylines(self.current_fish)
            
            # Draw seed name if provided
            if seed:
                self.draw_text(10, 115, f"Seed: {seed[:20]}", scale=1)
            
            self.draw_text(200, 115, f"#{self.fish_count}", scale=1)
            
            # Update display
            self.update_display()
            
            self.fish_count += 1
            print("  Done!")
            
        except Exception as e:
            print(f"Error generating fish: {e}")
            import traceback
            traceback.print_exc()
        
        # Free memory
        gc.collect()
    
    def save_current_fish(self):
        """Save current fish as SVG"""
        if not self.current_fish:
            print("No fish to save")
            return
        
        try:
            svg = draw_svg(self.current_fish, self.width, self.height)
            filename = f"fish_{self.fish_count}.svg"
            
            # Try to write to filesystem
            try:
                with open(filename, 'w') as f:
                    f.write(svg)
                print(f"Saved to {filename}")
            except:
                print("Filesystem not available")
        
        except Exception as e:
            print(f"Error saving fish: {e}")
    
    def run_demo(self):
        """Run demo mode with several fish"""
        seeds = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
        
        for seed in seeds:
            print(f"\n=== Fish: {seed} ===")
            self.generate_new_fish(seed)
            
            if BADGER_AVAILABLE:
                # Wait a bit on real hardware
                time.sleep(2)
            else:
                # Wait a bit in demo mode
                time.sleep(1)
    
    def run_interactive(self):
        """Run interactive mode on Badger2040"""
        print("\n=== FishDraw for Badger2040 ===")
        print("Starting interactive mode...\n")
        
        # Generate first fish
        self.generate_new_fish()
        
        if BADGER_AVAILABLE:
            print("\nButton controls:")
            print("  A - New random fish")
            print("  B - Save current fish")
            print("  C - Show info")
            print("  D - Power off")
            
            try:
                while True:
                    if self.badger.pressed(badger2040.UP):
                        print("UP pressed - skipped")
                    elif self.badger.pressed(badger2040.A):
                        self.generate_new_fish()
                    elif self.badger.pressed(badger2040.B):
                        self.save_current_fish()
                    elif self.badger.pressed(badger2040.C):
                        print(f"Fish #{self.fish_count}: {self.current_seed}")
                    elif self.badger.pressed(badger2040.D):
                        print("Powering off...")
                        self.badger.halt()
                    
                    time.sleep(0.1)
            
            except KeyboardInterrupt:
                print("\nInterrupted")
        
        else:
            print("\nSimulation mode - generating demo fish...")
            self.run_demo()


def main():
    """Main entry point"""
    print("=" * 40)
    print("FishDraw for Badger2040")
    print("=" * 40)
    
    app = FishDrawApp()
    
    if BADGER_AVAILABLE:
        print("Badger2040 detected!")
        app.run_interactive()
    else:
        print("Badger2040 not detected - demo mode")
        app.run_demo()


if __name__ == "__main__":
    main()
