"""
Main entry point for the modular vehicle detection and tracking system.
"""

from vehicle_tracker import VehicleTracker
from detection_config import *

def main():
    """Main function to run vehicle detection and tracking."""
    # Configuration
    video_path = DEFAULT_INPUT_VIDEO
    model_path = DEFAULT_MODEL_PATH
    output_video_path = DEFAULT_OUTPUT_VIDEO
    output_csv_path = DEFAULT_OUTPUT_CSV
    
    print("=== DriveTRACE Vehicle Detection & Tracking ===")
    print(f"Input video: {video_path}")
    print(f"YOLO model: {model_path}")
    print(f"Output video: {output_video_path}")
    print(f"Output CSV: {output_csv_path}")
    print("=" * 50)
    
    # Create and run tracker
    tracker = VehicleTracker(
        video_path=video_path,
        model_path=model_path,
        output_video_path=output_video_path,
        output_csv_path=output_csv_path
    )
    
    tracker.run()

if __name__ == "__main__":
    main()
