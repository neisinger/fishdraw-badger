"""
FishDraw for Badger2040
Display driver and integration for Pimoroni Badger2040 e-ink display
"""

import gc
import json
import random
import time
from fishdraw_complete import main, draw_svg, str_to_seed, binomen

class BadgerFish:
    """FishDraw controller for Badger2040"""
    
    def __init__(self, config_path="config.json"):
        """Initialize Badger2040 display and load configuration"""
        # Load configuration
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"Config file not found, using defaults")
            self.config = {
                "seed_step": 10,
                "history_size": 20,
                "button_delay_ms": 200,
                "display_width": 296,
                "display_height": 128,
                "simulation_mode": True
            }
        
        self.DISPLAY_WIDTH = self.config.get("display_width", 296)
        self.DISPLAY_HEIGHT = self.config.get("display_height", 128)
        self.SEED_STEP = self.config.get("seed_step", 10)
        self.HISTORY_SIZE = self.config.get("history_size", 20)
        self.BUTTON_DELAY = self.config.get("button_delay_ms", 200) / 1000.0
        
        # Initialize display
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
            # Get button constants from badger2040 module
            self.button_a = badger2040.BUTTON_A
            self.button_b = badger2040.BUTTON_B
            self.button_c = badger2040.BUTTON_C
            self.button_up = badger2040.BUTTON_UP
            self.button_down = badger2040.BUTTON_DOWN
            self.has_display = True
            print("✓ Badger2040 display initialized")
        except ImportError:
            print("Badger2040 library not found - running in simulation mode")
        except Exception as e:
            print(f"Error initializing Badger2040: {e}")
        
        # History and state management
        self.history = []  # List of generated fish seeds
        self.current_history_index = -1  # Index in history
        self.current_seed = None
        self.current_drawing = None
        self.last_button_time = 0
    
    def load_config(self, path="config.json"):
        """Load configuration from JSON file"""
        try:
            with open(path, 'r') as f:
                self.config = json.load(f)
                self.SEED_STEP = self.config.get("seed_step", 10)
                self.HISTORY_SIZE = self.config.get("history_size", 20)
                self.BUTTON_DELAY = self.config.get("button_delay_ms", 200) / 1000.0
                print(f"✓ Loaded config: step={self.SEED_STEP}, history_size={self.HISTORY_SIZE}")
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def draw_polylines(self, polylines, thickness=1):
        """Draw polylines on the display"""
        if not self.has_display:
            print(f"Display simulation: Would draw {len(polylines)} polylines")
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
                        self.badger.pixel(px, py)
            
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
        if seed is None:
            seed = binomen()
        
        print(f"Generating fish: {seed}...")
        drawing = main(seed, self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)
        print(f"Generated {len(drawing)} polylines")
        
        print("Drawing to display...")
        self.draw_polylines(drawing, thickness=1)
        
        # Store in history
        self.current_seed = seed
        self.current_drawing = drawing
        if seed not in self.history:
            self.history.append(seed)
            if len(self.history) > self.HISTORY_SIZE:
                self.history.pop(0)
        self.current_history_index = self.history.index(seed)
        
        print("Done!")
        gc.collect()
    
    def _can_press_button(self):
        """Check if enough time has passed since last button press"""
        current_time = time.time()
        if current_time - self.last_button_time >= self.BUTTON_DELAY:
            self.last_button_time = current_time
            return True
        return False
    
    def button_a_pressed(self):
        """Button A: Decrease seed by SEED_STEP"""
        if not self._can_press_button():
            return
        
        if self.current_seed is None:
            self.generate_and_display(binomen())
            return
        
        # Try to parse seed as number
        try:
            seed_num = int(self.current_seed)
        except ValueError:
            # If not a number, try to use hash
            seed_num = str_to_seed(self.current_seed)
        
        new_seed_num = seed_num - self.SEED_STEP
        if new_seed_num < 0:
            new_seed_num = 0
        
        new_seed = str(new_seed_num)
        print(f"Button A: {self.current_seed} -> {new_seed}")
        self.generate_and_display(new_seed)
    
    def button_b_pressed(self):
        """Button B: Random seed"""
        if not self._can_press_button():
            return
        
        new_seed = binomen()
        print(f"Button B: Random seed -> {new_seed}")
        self.generate_and_display(new_seed)
    
    def button_c_pressed(self):
        """Button C: Increase seed by SEED_STEP"""
        if not self._can_press_button():
            return
        
        if self.current_seed is None:
            self.generate_and_display(binomen())
            return
        
        # Try to parse seed as number
        try:
            seed_num = int(self.current_seed)
        except ValueError:
            # If not a number, try to use hash
            seed_num = str_to_seed(self.current_seed)
        
        new_seed_num = seed_num + self.SEED_STEP
        new_seed = str(new_seed_num)
        print(f"Button C: {self.current_seed} -> {new_seed}")
        self.generate_and_display(new_seed)
    
    def button_up_pressed(self):
        """Button Up: Previous fish in history"""
        if not self._can_press_button():
            return
        
        if not self.history:
            print("No history available")
            return
        
        new_index = self.current_history_index - 1
        if new_index < 0:
            new_index = len(self.history) - 1
        
        self.current_history_index = new_index
        seed = self.history[new_index]
        print(f"History Up: [{new_index + 1}/{len(self.history)}] {seed}")
        self.generate_and_display(seed)
    
    def button_down_pressed(self):
        """Button Down: Next fish in history"""
        if not self._can_press_button():
            return
        
        if not self.history:
            print("No history available")
            return
        
        new_index = self.current_history_index + 1
        if new_index >= len(self.history):
            new_index = 0
        
        self.current_history_index = new_index
        seed = self.history[new_index]
        print(f"History Down: [{new_index + 1}/{len(self.history)}] {seed}")
        self.generate_and_display(seed)
    
    def print_status(self):
        """Print current status"""
        status = f"""
╔════════════════════════════════════════════╗
║           FishDraw for Badger2040          ║
╚════════════════════════════════════════════╝
Current Seed:      {self.current_seed or 'None'}
History Size:      {len(self.history)}/{self.HISTORY_SIZE}
History Index:     {self.current_history_index + 1}/{len(self.history)} (if available)
Seed Step:         {self.SEED_STEP}
Display:           {self.DISPLAY_WIDTH}x{self.DISPLAY_HEIGHT}
Has Display:       {self.has_display}

Button Controls:
  A: Seed - {self.SEED_STEP}
  B: Random Seed
  C: Seed + {self.SEED_STEP}
  UP: Previous Fish (History)
  DOWN: Next Fish (History)
"""
        print(status)
    
    def interactive_mode(self):
        """Interactive mode with button simulation"""
        print("Interactive mode - Simulating button presses")
        print("Commands: a(button_a), b(button_b), c(button_c), u(up), d(down), s(status), q(quit)")
        
        # Generate initial fish
        self.generate_and_display(binomen())
        
        while True:
            try:
                cmd = input("\nCommand> ").strip().lower()
                
                if cmd == 'a':
                    self.button_a_pressed()
                elif cmd == 'b':
                    self.button_b_pressed()
                elif cmd == 'c':
                    self.button_c_pressed()
                elif cmd == 'u':
                    self.button_up_pressed()
                elif cmd == 'd':
                    self.button_down_pressed()
                elif cmd == 's':
                    self.print_status()
                elif cmd == 'q':
                    print("Exiting...")
                    break
                else:
                    print("Unknown command. Try: a, b, c, u, d, s, or q")
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def run(self):
        """Main run loop for Badger2040"""
        print("FishDraw for Badger2040")
        print("=" * 40)
        self.print_status()
        
        if self.has_display and self.badger:
            print("\nBadger2040 detected!")
            print("Button mapping:")
            print("  A - Decrease seed")
            print("  B - Random seed")
            print("  C - Increase seed")
            print("  UP - Previous fish")
            print("  DOWN - Next fish")
            
            # Generate initial fish
            self.generate_and_display(binomen())
            
            # Main loop with button handling
            try:
                while True:
                    # Check buttons using badger2040 constants
                    if self.button_up is not None and self.badger.pressed(self.button_up):
                        self.button_up_pressed()
                        time.sleep(self.BUTTON_DELAY)
                    elif self.button_down is not None and self.badger.pressed(self.button_down):
                        self.button_down_pressed()
                        time.sleep(self.BUTTON_DELAY)
                    elif self.button_a is not None and self.badger.pressed(self.button_a):
                        self.button_a_pressed()
                        time.sleep(self.BUTTON_DELAY)
                    elif self.button_b is not None and self.badger.pressed(self.button_b):
                        self.button_b_pressed()
                        time.sleep(self.BUTTON_DELAY)
                    elif self.button_c is not None and self.badger.pressed(self.button_c):
                        self.button_c_pressed()
                        time.sleep(self.BUTTON_DELAY)
                    
                    time.sleep(0.05)  # Small delay to prevent CPU spinning
            except KeyboardInterrupt:
                print("\nExiting...")
                try:
                    self.badger.clear()
                    self.badger.update()
                except:
                    pass
        else:
            print("\nRunning in simulation mode (interactive)")
            self.interactive_mode()


def main_badger():
    """Main entry point for Badger2040"""
    badger_fish = BadgerFish(config_path="config.json")
    badger_fish.run()


if __name__ == "__main__":
    main_badger()


