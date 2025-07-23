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
