"""
Main entry point for the modular vehicle detection and tracking system.
"""

from vehicle_tracker import VehicleTracker
from detection_config import *
from detection_utils import parse_time_string

def get_time_range_from_config():
    """
    Get time range from configuration, handling both seconds and string formats.
    
    Returns:
        tuple: (start_time_seconds, end_time_seconds)
    """
    start_time = START_TIME_SECONDS
    end_time = END_TIME_SECONDS
    
    # If string format is provided, parse it
    if START_TIME_STRING is not None:
        try:
            start_time = parse_time_string(START_TIME_STRING)
        except ValueError as e:
            print(f"Warning: Invalid start time format '{START_TIME_STRING}': {e}")
            start_time = None
    
    if END_TIME_STRING is not None:
        try:
            end_time = parse_time_string(END_TIME_STRING)
        except ValueError as e:
            print(f"Warning: Invalid end time format '{END_TIME_STRING}': {e}")
            end_time = None
    
    return start_time, end_time

def main():
    """Main function to run vehicle detection and tracking."""
    # Configuration
    video_path = DEFAULT_INPUT_VIDEO
    model_path = DEFAULT_MODEL_PATH
    output_video_path = DEFAULT_OUTPUT_VIDEO
    output_csv_path = DEFAULT_OUTPUT_CSV
    
    # Get time range settings
    start_time, end_time = get_time_range_from_config()
    
    print("=== DriveTRACE Vehicle Detection & Tracking ===")
    print(f"Input video: {video_path}")
    print(f"YOLO model: {model_path}")
    print(f"Output video: {output_video_path}")
    print(f"Output CSV: {output_csv_path}")
    
    if start_time is not None or end_time is not None:
        from detection_utils import format_seconds_to_time
        start_str = format_seconds_to_time(start_time) if start_time is not None else "0:00"
        end_str = format_seconds_to_time(end_time) if end_time is not None else "End"
        print(f"Time range: {start_str} to {end_str}")
    else:
        print("Processing: Entire video")
    
    print("=" * 50)
    
    # Create and run tracker
    tracker = VehicleTracker(
        video_path=video_path,
        model_path=model_path,
        output_video_path=output_video_path,
        output_csv_path=output_csv_path,
        start_time=start_time,
        end_time=end_time
    )
    
    tracker.run()

if __name__ == "__main__":
    main()
