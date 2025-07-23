"""
Configuration settings for vehicle detection and tracking system.
"""

# Video processing settings
DEFAULT_MODEL_PATH = "Detection/yolov8m.pt"
DEFAULT_INPUT_VIDEO = "Detection/test_footage/5.mp4"
DEFAULT_OUTPUT_VIDEO = "Detection/annotated_test1.mp4"
DEFAULT_OUTPUT_CSV = "Detection/traffic_simulation_data.csv"

# Time range settings for video processing
# Set to None to process entire video, or specify in seconds
START_TIME_SECONDS = None  # Start time in seconds (e.g., 30 for 0:30)
END_TIME_SECONDS = None    # End time in seconds (e.g., 80 for 1:20)

# Alternative: specify time ranges as "MM:SS" format
START_TIME_STRING = "0:00"   # e.g., "0:30" or "1:15"
END_TIME_STRING = "0:10"     # e.g., "1:20" or "2:45"

# Detection settings
VEHICLE_CLASS_IDS = [2, 3, 5, 7]  # cars, trucks, buses, motorcycles in COCO dataset

# ROI settings (as fractions of frame dimensions)
ROI_RELATIVE_POINTS = [
    (0.2, 0.2),  # Top-left
    (0.8, 0.2),  # Top-right
    (0.8, 0.8),  # Bottom-right
    (0.2, 0.8)   # Bottom-left
]

# Perspective transform destination points
PERSPECTIVE_DST_POINTS = [
    (0, 0),
    (400, 0),
    (400, 600),
    (0, 600)
]

# Speed calculation settings
SIMULATION_SPEED_RANGE = (0, 600)  # Min and max speeds for simulation
DEFAULT_SIMULATION_SPEED = 300
BASE_SIMULATION_SPEED = 200
SPEED_SCALE_FACTOR = 3

# Video codec settings
PRIMARY_CODEC = 'avc1'  # H.264
FALLBACK_CODEC = 'mp4v'

# Annotation settings
BOX_THICKNESS = 2
TRACE_LENGTH = 75
FONT_SCALE = 0.5
FONT_THICKNESS = 2

# Progress reporting
PROGRESS_UPDATE_INTERVAL = 30  # frames
