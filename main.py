"""
FishDraw for Badger2040 - Main entry point
Simply copy this file to your Badger2040 and it will run automatically on startup
"""

from badger2040_fish import BadgerFish

# Start the application
badger_fish = BadgerFish(config_path="config.json")
badger_fish.run()
