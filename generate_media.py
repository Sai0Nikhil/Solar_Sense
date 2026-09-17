import os
import sys
import time
import subprocess
import urllib.request
from PIL import Image

python_exe = sys.executable
chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
screenshot_dir = r"c:\Ml_Project\Solar_Sense\screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

print("Starting Flask app...")
server = subprocess.Popen(
    [python_exe, "flask_project/app.py"],
    cwd=r"c:\Ml_Project\Solar_Sense",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

base_url = "http://127.0.0.1:5000"

# Wait for server to respond
ready = False
for i in range(25):
    try:
        with urllib.request.urlopen(base_url, timeout=2) as resp:
            if resp.status == 200:
                ready = True
                print("Server ready!")
                break
    except Exception:
        time.sleep(1.5)

if not ready:
    print("Failed to connect to Flask server")
    server.terminate()
    sys.exit(1)

# Trigger a predict POST first to warm up and verify
import urllib.parse
post_data = urllib.parse.urlencode({
    "model_name": "HistGradientBoosting",
    "IRRADIATION": "0.85",
    "MODULE_TEMPERATURE": "52.0",
    "AMBIENT_TEMPERATURE": "36.0",
    "TEMP_DIFF": "16.0",
    "HOUR": "12",
    "MINUTE": "30"
}).encode("utf-8")

req = urllib.request.Request(f"{base_url}/predict", data=post_data, method="POST")
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print("Warmup POST to /predict succeeded:", resp.status)
except Exception as e:
    print("POST /predict warmup error:", e)

pages = [
    ("home.png", f"{base_url}/"),
    ("missing.png", f"{base_url}/missing"),
    ("visualize.png", f"{base_url}/visualize"),
    ("train.png", f"{base_url}/train"),
    ("evaluate.png", f"{base_url}/evaluate"),
    ("predict.png", f"{base_url}/predict?sample=1"),
]

captured = []
for fname, url in pages:
    target = os.path.join(screenshot_dir, fname)
    cmd = [
        chrome_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1440,900",
        f"--screenshot={target}",
        url
    ]
    print(f"Capturing {fname} from {url}...")
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=30)
    except subprocess.TimeoutExpired:
        print(f"  Timeout capturing {fname}")
    time.sleep(1.5)
    if os.path.exists(target) and os.path.getsize(target) > 1000:
        print(f"  Saved {fname} ({os.path.getsize(target):,} bytes)")
        captured.append(target)
    else:
        print(f"  Warning: {fname} missing or too small")

# Clean up server
server.terminate()
print("Flask server stopped.")

# Now create demo.gif
gif_path = os.path.join(screenshot_dir, "demo.gif")
print("Generating demo.gif from captured screenshots...")

# Preferred sequence for the walkthrough GIF:
# 1. Home (Telemetry Overview & KPIs)
# 2. Missing Value Analysis & Imputation Lab
# 3. Data Visualization (Diurnal, Distributions, IPI ranking)
# 4. Model Training Candidates
# 5. Model Evaluation (Sealed holdout, Scatter, Attributions)
# 6. Prediction Engine (Inference & Feature Impact)

frames = []
for target in captured:
    if os.path.exists(target):
        img = Image.open(target).convert("RGB")
        # Scale to clean presentation resolution (1024 x 640)
        img_resized = img.resize((1024, 640), Image.Resampling.LANCZOS)
        # Repeat frame 3 times at 600ms = 1.8 seconds per slide
        for _ in range(3):
            frames.append(img_resized)

if frames:
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=600,
        loop=0,
        optimize=True
    )
    print(f"demo.gif created successfully at {gif_path} ({os.path.getsize(gif_path):,} bytes)!")
else:
    print("No frames available for demo.gif")

print("All screenshots & demo.gif generation completed successfully.")
