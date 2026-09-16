"""SolarSense — Build-time artifact pretrainer.

Run this script during Docker build / Render buildCommand to pretrain
and cache model artifacts for both plants so cold starts cost nothing.

Usage:
    python flask_project/train_artifact.py
"""
import sys
import os

# Make flask_project importable when run from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import model

for plant_num in (1, 2):
    print(f"[SolarSense] Pretraining Plant {plant_num} models …")
    try:
        bundle = model.save_artifact(plant_num)
        champ = bundle["best"]
        r2 = next(m["metrics"]["r2"] for m in bundle["models"] if m["name"] == champ)
        print(f"[SolarSense] Plant {plant_num} done — champion: {champ}, R²={r2}")
    except Exception as e:
        print(f"[SolarSense] Plant {plant_num} pretraining failed: {e}")
        sys.exit(1)

print("[SolarSense] All artifacts pretrained successfully.")
