"""Precompute SolarSense models for Plant 1 and Plant 2."""
import os
import sys

# Ensure flask_project is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import model

if __name__ == "__main__":
    print("Training and caching artifacts for Plant 1...")
    model.save_artifact(plant_num=1)
    print("Plant 1 artifact written.")

    print("Training and caching artifacts for Plant 2...")
    model.save_artifact(plant_num=2)
    print("Plant 2 artifact written.")
    print("All artifacts successfully generated!")
