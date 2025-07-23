"""
Utility functions for the vehicle detection system.
"""

import os
import sys
from pathlib import Path

def ensure_directory_exists(file_path):
    """
    Ensure that the directory for a file path exists.
    
    Args:
        file_path: Path to a file
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def validate_file_extension(file_path, allowed_extensions):
    """
    Validate that a file has an allowed extension.
    
    Args:
        file_path: Path to the file
        allowed_extensions: List of allowed extensions (e.g., ['.mp4', '.avi'])
        
    Returns:
        bool: True if extension is allowed
    """
    file_ext = Path(file_path).suffix.lower()
    return file_ext in [ext.lower() for ext in allowed_extensions]

def get_file_size_mb(file_path):
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        float: File size in MB
    """
    if not os.path.exists(file_path):
        return 0
    return os.path.getsize(file_path) / (1024 * 1024)

def print_system_info():
    """Print system and environment information."""
    print("System Information:")
    print(f"  Python version: {sys.version}")
    print(f"  Working directory: {os.getcwd()}")
    
def format_time(seconds):
    """
    Format seconds into human-readable time.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        str: Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.1f}s"

def parse_time_string(time_string):
    """
    Parse time string in format "MM:SS" or "H:MM:SS" to seconds.
    
    Args:
        time_string: Time in format "MM:SS" (e.g., "1:20") or "H:MM:SS" (e.g., "1:05:30")
        
    Returns:
        float: Time in seconds
        
    Raises:
        ValueError: If time string format is invalid
    """
    if not time_string:
        return None
    
    try:
        parts = time_string.split(':')
        
        if len(parts) == 2:  # MM:SS format
            minutes, seconds = map(float, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:  # H:MM:SS format
            hours, minutes, seconds = map(float, parts)
            return hours * 3600 + minutes * 60 + seconds
        else:
            raise ValueError("Time format must be MM:SS or H:MM:SS")
    except ValueError as e:
        raise ValueError(f"Invalid time format '{time_string}': {e}")

def format_seconds_to_time(seconds):
    """
    Format seconds back to MM:SS or H:MM:SS format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        str: Formatted time string
    """
    if seconds < 3600:  # Less than 1 hour
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    else:  # 1 hour or more
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}:{minutes:02d}:{secs:02d}"

def validate_time_range(start_time, end_time, video_duration):
    """
    Validate that time range is valid for video duration.
    
    Args:
        start_time: Start time in seconds
        end_time: End time in seconds
        video_duration: Total video duration in seconds
        
    Returns:
        tuple: (validated_start, validated_end, is_valid)
    """
    if start_time is None:
        start_time = 0
    if end_time is None:
        end_time = video_duration
    
    # Validate bounds
    start_time = max(0, start_time)
    end_time = min(video_duration, end_time)
    
    # Ensure start < end
    if start_time >= end_time:
        return start_time, end_time, False
    
    return start_time, end_time, True

class ProgressTracker:
    """Simple progress tracking utility."""
    
    def __init__(self, total_items, update_interval=10):
        self.total_items = total_items
        self.update_interval = update_interval
        self.current_item = 0
        self.start_time = None
    
    def start(self):
        """Start tracking progress."""
        import time
        self.start_time = time.time()
        self.current_item = 0
    
    def update(self, items_processed=1):
        """Update progress."""
        import time
        self.current_item += items_processed
        
        if self.current_item % self.update_interval == 0 or self.current_item >= self.total_items:
            if self.start_time:
                elapsed = time.time() - self.start_time
                progress_pct = (self.current_item / self.total_items) * 100
                rate = self.current_item / elapsed if elapsed > 0 else 0
                
                if self.current_item < self.total_items:
                    eta = (self.total_items - self.current_item) / rate if rate > 0 else 0
                    print(f"\rProgress: {self.current_item}/{self.total_items} ({progress_pct:.1f}%) - {rate:.1f}/s - ETA: {format_time(eta)}", end="")
                else:
                    print(f"\rCompleted: {self.current_item}/{self.total_items} ({progress_pct:.1f}%) - Total time: {format_time(elapsed)}")
    
    def finish(self):
        """Finish progress tracking."""
        if self.current_item < self.total_items:
            self.current_item = self.total_items
            self.update(0)
        print()  # New line
