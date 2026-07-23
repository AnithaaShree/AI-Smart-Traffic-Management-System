# config.py
# Central configuration file for the Smart Traffic Management System.
# Change video paths, thresholds, and timing settings here.

# ── Video Scenario Paths ────────────────────────────────────────────────────
VIDEOS = {
    "Low Traffic":        "videos/traffic_low.mp4",
    "Medium Traffic":     "videos/traffic_medium.mp4",
    "High Traffic":       "videos/traffic_high.mp4",
    "Ambulance Detect":   "videos/traffic_ambulance.mp4",
    "Violation Detect":   "videos/traffic_violation.mp4",
}

# Default video to load on startup
DEFAULT_VIDEO = "Low Traffic"

# ── Detection Settings ──────────────────────────────────────────────────────
YOLO_MODEL        = "yolov8n.pt"   # YOLOv8 nano — fast and lightweight
CONFIDENCE_THRESH = 0.35           # Minimum confidence to count a detection
FRAME_SKIP        = 2              # Process every Nth frame (higher = faster)

# ── Vehicle Class IDs (COCO dataset) ───────────────────────────────────────
VEHICLE_CLASS_IDS = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

# ── Traffic Density Thresholds ──────────────────────────────────────────────
DENSITY_LOW_MAX    = 5    # 0–5 vehicles  → Low
DENSITY_MEDIUM_MAX = 15   # 6–15 vehicles → Medium
                          # 16+           → High

# ── Signal Timing (seconds) ────────────────────────────────────────────────
GREEN_LOW        = 10
GREEN_MEDIUM     = 20
GREEN_HIGH       = 40
GREEN_AMBULANCE  = 60
YELLOW_DURATION  = 3
RED_DURATION     = 10

# ── Stop Line Position ──────────────────────────────────────────────────────
# Fraction of frame height where stop line is drawn (0.0 = top, 1.0 = bottom)
STOP_LINE_RATIO  = 0.65

# ── Ambulance Simulation ────────────────────────────────────────────────────
# When using traffic_ambulance.mp4, simulate ambulance from frame 80 to 200
AMBULANCE_SIM_START = 80
AMBULANCE_SIM_END   = 200

# ── GUI Settings ────────────────────────────────────────────────────────────
VIDEO_DISPLAY_WIDTH  = 720
VIDEO_DISPLAY_HEIGHT = 520
WINDOW_SIZE          = "1200x750"