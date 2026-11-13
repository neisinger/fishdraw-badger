"""
FishDraw for Badger2040
Display driver and integration for Pimoroni Badger2040 e-ink display
"""

import gc
import json
import random
import time
from fishdraw import generate_fish, generate_name

class BadgerFish:
    """FishDraw controller for Badger2040"""
    
    def __init__(self, config_path="config.json"):
        """Initialize Badger2040 display and load configuration"""
        self.load_config(config_path)
        
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
            self.button_a = badger2040.BUTTON_A
            self.button_b = badger2040.BUTTON_B
            self.button_c = badger2040.BUTTON_C
            self.button_up = badger2040.BUTTON_UP
            self.button_down = badger2040.BUTTON_DOWN
            self.has_display = True
            print("✓ Badger2040 display initialized")
        except Exception as e:
            print(f"Display not available: {e}")
        
        # History and state
        self.history = []
        self.current_history_index = -1
        self.current_seed = None
        self.current_name = None
        self.current_drawing = None
        self.last_button_time = 0
    
    def load_config(self, path="config.json"):
        """Load configuration from JSON file"""
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
        """Draw polylines on the display"""
        if not self.has_display:
            print(f"Sim: {len(polylines)} polylines")
            return
        
        # Clear display
        self.badger.clear()
        
        # Draw each polyline
        for polyline in polylines:
            if len(polyline) < 2:
                continue
            
            for i in range(len(polyline) - 1):
                x0 = int(polyline[i][0])
                y0 = int(polyline[i][1])
                x1 = int(polyline[i + 1][0])
                y1 = int(polyline[i + 1][1])
                
                # Draw line on display
                self.badger.line(x0, y0, x1, y1, 1, 1)
        
        # Update display
        self.badger.update()
    
    def generate_and_display(self, seed=None):
        """Generate a fish and display it"""
        if seed is None:
            seed = int(random.random() * 1000000)
        
        # Generate fish
        print(f"Generating fish: {seed}...")
        polylines = generate_fish(seed, self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)
        print(f"Generated {len(polylines)} polylines")
        
        # Draw to display
        print("Drawing to display...")
        self.draw_polylines(polylines)
        
        # Store in history
        self.current_seed = seed
        self.current_drawing = polylines
        self.current_name = generate_name()
        
        # Add to history
        if seed not in self.history:
            self.history.append(seed)
            if len(self.history) > self.HISTORY_SIZE:
                self.history.pop(0)
        
        self.current_history_index = self.history.index(seed)
        print(f"Done! Name: {self.current_name}")
    
    def show_status(self):
        """Show current status"""
        if self.has_display:
            self.badger.clear()
            self.badger.text("FishDraw for Badger2040", 0, 0, scale=1)
            self.badger.text(f"Seed: {self.current_seed}", 0, 15, scale=1)
            self.badger.text(f"Name: {self.current_name}", 0, 30, scale=1)
            self.badger.text(f"History: {len(self.history)}/{self.HISTORY_SIZE}", 0, 45, scale=1)
            self.badger.update()
        else:
            print(f"Seed: {self.current_seed}")
            print(f"Name: {self.current_name}")
            print(f"History: {len(self.history)}/{self.HISTORY_SIZE}")
    
    def button_a_pressed(self):
        """Decrease seed"""
        if self.current_seed is not None:
            self.generate_and_display(self.current_seed - self.SEED_STEP)
    
    def button_b_pressed(self):
        """Random seed"""
        self.generate_and_display()
    
    def button_c_pressed(self):
        """Increase seed"""
        if self.current_seed is not None:
            self.generate_and_display(self.current_seed + self.SEED_STEP)
    
    def button_up_pressed(self):
        """Previous fish in history"""
        if self.history and self.current_history_index > 0:
            self.current_history_index -= 1
            self.generate_and_display(self.history[self.current_history_index])
    
    def button_down_pressed(self):
        """Next fish in history"""
        if self.history and self.current_history_index < len(self.history) - 1:
            self.current_history_index += 1
            self.generate_and_display(self.history[self.current_history_index])
    
    def run(self):
        """Main loop"""
        print("\nStarting FishDraw...\n")
        
        if not self.has_display:
            print("Running in simulation mode")
            self.generate_and_display()
            return
        
        # Generate first fish
        self.generate_and_display()
        
        # Main loop
        while True:
            now = time.time()
            
            if now - self.last_button_time < self.BUTTON_DELAY:
                time.sleep(0.01)
                continue
            
            # Check buttons
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
