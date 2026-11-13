"""
FishDraw for Badger2040 - Main entry point
Place this as /main.py on the Badger2040

Button mappings (Badger2040 actual hardware):
  A      = Generate new fish
  B      = Toggle style (normal/aggressive/elegant)
  C      = Show current fish info
  UP     = Increase fish scale
  DOWN   = Decrease fish scale
"""

import gc
import time

try:
    import badger2040
    BADGER_AVAILABLE = True
except ImportError:
    BADGER_AVAILABLE = False
    print("Running in simulation mode (no Badger2040 hardware)")

from fishdraw_complete import main as generate_fish


class FishDrawApp:
    """Main application for Badger2040"""
    
    def __init__(self):
        if BADGER_AVAILABLE:
            self.badger = badger2040.Badger2040()
            self.width = 296
            self.height = 128
            self.display = self.badger
        else:
            self.badger = None
            self.width = 296
            self.height = 128
            self.display = None
        
        self.current_fish = None
        self.current_seed = None
        self.fish_count = 0
        self.style_idx = 0  # 0=normal, 1=aggressive, 2=elegant
        self.scale = 1.0
        self.show_info = False
        
        # Style parameters
        self.styles = [
            {"name": "Normal", "body_fat": 0.5, "fin_length": 1.0},
            {"name": "Aggressive", "body_fat": 0.3, "fin_length": 1.5},
            {"name": "Elegant", "body_fat": 0.7, "fin_length": 0.8},
        ]
    
    def clear_display(self):
        """Clear the display"""
        if not self.badger:
            return
        self.badger.clear()
    
    def draw_line(self, x1, y1, x2, y2):
        """Draw a line using Bresenham algorithm"""
        if not self.badger:
            return
        
        # Simple line drawing using badger's draw methods
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        while True:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.badger.pixel(x, y, 1)
            
            if x == x2 and y == y2:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def draw_polyline(self, points):
        """Draw a polyline (list of (x,y) tuples)"""
        if not points or len(points) < 2:
            return
        
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            self.draw_line(int(x1), int(y1), int(x2), int(y2))
    
    def draw_fish_on_display(self, fish_data):
        """Draw the fish on the display"""
        if not self.badger:
            return
        
        self.clear_display()
        
        # Offset to center fish on display
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Draw all polylines from the fish data
        if isinstance(fish_data, dict) and 'polylines' in fish_data:
            for polyline in fish_data['polylines']:
                # Scale and offset points
                scaled_points = []
                for x, y in polyline:
                    sx = center_x + (x * self.scale)
                    sy = center_y + (y * self.scale)
                    scaled_points.append((sx, sy))
                
                self.draw_polyline(scaled_points)
        
        # Draw status line if showing info
        if self.show_info:
            style_name = self.styles[self.style_idx]["name"]
            # Simple text: just show info via print
            print(f"Fish #{self.fish_count} | Style: {style_name} | Scale: {self.scale:.1f}")
        
        self.badger.update()
    
    def generate_new_fish(self, seed=None):
        """Generate a new random fish"""
        self.fish_count += 1
        
        if seed is None:
            # Generate from current count + style as seed
            seed = f"Fish_{self.fish_count}_S{self.style_idx}"
        
        self.current_seed = seed
        
        # Get current style parameters
        style = self.styles[self.style_idx]
        
        # Generate fish with parameters
        params = {
            "seed": seed,
            "body_fat": style["body_fat"],
            "fin_length": style["fin_length"],
            "scale": self.scale * 20,  # Scale from 0-2 range to pixel range
        }
        
        try:
            # Generate the fish
            self.current_fish = generate_fish(seed=seed)
            
            # Draw on display
            if self.badger:
                self.draw_fish_on_display(self.current_fish)
            
            print(f"✓ Fish #{self.fish_count}: {seed}")
            
            # Free memory
            gc.collect()
            
        except Exception as e:
            print(f"Error generating fish: {e}")
    
    def cycle_style(self):
        """Cycle through fish styles"""
        self.style_idx = (self.style_idx + 1) % len(self.styles)
        style = self.styles[self.style_idx]
        print(f"Style: {style['name']}")
        self.generate_new_fish()
    
    def increase_scale(self):
        """Increase fish scale"""
        self.scale = min(self.scale + 0.2, 2.0)
        print(f"Scale: {self.scale:.1f}")
        if self.current_fish:
            self.draw_fish_on_display(self.current_fish)
    
    def decrease_scale(self):
        """Decrease fish scale"""
        self.scale = max(self.scale - 0.2, 0.5)
        print(f"Scale: {self.scale:.1f}")
        if self.current_fish:
            self.draw_fish_on_display(self.current_fish)
    
    def toggle_info(self):
        """Toggle info display"""
        self.show_info = not self.show_info
        if self.current_fish:
            self.draw_fish_on_display(self.current_fish)
    
    def run_demo(self):
        """Run demo mode with several fish"""
        print("\n=== Demo Mode ===")
        seeds = ["Alpha", "Beta", "Gamma"]
        
        for i, seed in enumerate(seeds):
            print(f"\nGenerating fish: {seed}")
            self.style_idx = i % len(self.styles)
            self.generate_new_fish(seed)
            time.sleep(2)
    
    def run_interactive(self):
        """Run interactive mode on Badger2040"""
        print("\n" + "=" * 40)
        print("FishDraw for Badger2040")
        print("=" * 40)
        print("\nButton controls:")
        print("  A      = New random fish")
        print("  B      = Cycle style (Normal/Aggressive/Elegant)")
        print("  C      = Toggle info display")
        print("  UP     = Increase scale")
        print("  DOWN   = Decrease scale")
        print("\nStarting...\n")
        
        # Generate first fish
        self.generate_new_fish()
        
        if BADGER_AVAILABLE:
            try:
                last_button_time = time.time()
                debounce_delay = 0.3  # Seconds between button presses
                
                while True:
                    current_time = time.time()
                    
                    # Check buttons with debouncing
                    if current_time - last_button_time > debounce_delay:
                        
                        if self.badger.is_pressed(badger2040.BUTTON_A):
                            print("→ Button A: New fish")
                            self.generate_new_fish()
                            last_button_time = current_time
                        
                        elif self.badger.is_pressed(badger2040.BUTTON_B):
                            print("→ Button B: Change style")
                            self.cycle_style()
                            last_button_time = current_time
                        
                        elif self.badger.is_pressed(badger2040.BUTTON_C):
                            print("→ Button C: Toggle info")
                            self.toggle_info()
                            last_button_time = current_time
                        
                        elif self.badger.is_pressed(badger2040.BUTTON_UP):
                            print("→ Button UP: Increase scale")
                            self.increase_scale()
                            last_button_time = current_time
                        
                        elif self.badger.is_pressed(badger2040.BUTTON_DOWN):
                            print("→ Button DOWN: Decrease scale")
                            self.decrease_scale()
                            last_button_time = current_time
                    
                    time.sleep(0.05)
            
            except KeyboardInterrupt:
                print("\n\nExiting...")
        
        else:
            print("Simulation mode - running demo...\n")
            self.run_demo()


def main():
    """Main entry point"""
    app = FishDrawApp()
    
    if BADGER_AVAILABLE:
        app.run_interactive()
    else:
        print("Badger2040 hardware not available.")
        print("Running simulation mode instead.\n")
        app.run_demo()


if __name__ == "__main__":
    main()
