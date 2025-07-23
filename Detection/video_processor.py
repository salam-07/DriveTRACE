"""
Video processing utilities for vehicle detection and annotation.
"""

import cv2
import time
from pathlib import Path
from detection_config import *

class VideoProcessor:
    def __init__(self, input_path, output_path, start_time=None, end_time=None):
        self.input_path = input_path
        self.output_path = output_path
        self.cap = None
        self.writer = None
        self.frame_width = 0
        self.frame_height = 0
        self.fps = 0
        self.total_frames = 0
        self.video_duration = 0
        
        # Time range settings
        self.start_time = start_time  # in seconds
        self.end_time = end_time      # in seconds
        self.start_frame = 0
        self.end_frame = 0
        self.processing_frames = 0
    
    def initialize(self):
        """Initialize video capture and writer."""
        # Initialize video capture
        self.cap = cv2.VideoCapture(self.input_path)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video file: {self.input_path}")
        
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_duration = self.total_frames / self.fps if self.fps > 0 else 0
        
        # Calculate frame range for processing
        self._calculate_frame_range()
        
        # Initialize video writer
        self._initialize_writer()
        
        print(f"Video initialized:")
        print(f"  Resolution: {self.frame_width}x{self.frame_height}")
        print(f"  FPS: {self.fps}")
        print(f"  Total frames: {self.total_frames}")
        print(f"  Video duration: {self._format_duration(self.video_duration)}")
        
        if self.start_time is not None or self.end_time is not None:
            print(f"  Processing range: {self._format_duration(self.start_time or 0)} to {self._format_duration(self.end_time or self.video_duration)}")
            print(f"  Processing frames: {self.start_frame} to {self.end_frame} ({self.processing_frames} frames)")
    
    def _calculate_frame_range(self):
        """Calculate the frame range to process based on time settings."""
        from detection_utils import validate_time_range
        
        # Validate and adjust time range
        start_time, end_time, is_valid = validate_time_range(
            self.start_time, self.end_time, self.video_duration
        )
        
        if not is_valid:
            raise ValueError(f"Invalid time range: start={start_time}, end={end_time}")
        
        self.start_time = start_time
        self.end_time = end_time
        
        # Convert time to frame numbers
        self.start_frame = int(start_time * self.fps)
        self.end_frame = int(end_time * self.fps)
        self.processing_frames = self.end_frame - self.start_frame
        
        # Ensure frame range is within bounds
        self.start_frame = max(0, self.start_frame)
        self.end_frame = min(self.total_frames, self.end_frame)
        self.processing_frames = self.end_frame - self.start_frame
    
    def _format_duration(self, seconds):
        """Format duration in seconds to readable format."""
        if seconds is None:
            return "N/A"
        from detection_utils import format_seconds_to_time
        return format_seconds_to_time(seconds)
    
    def _initialize_writer(self):
        """Initialize video writer with fallback codec support."""
        # Try primary codec first
        self.writer = cv2.VideoWriter(
            self.output_path,
            cv2.VideoWriter_fourcc(*PRIMARY_CODEC),
            self.fps,
            (self.frame_width, self.frame_height)
        )
        
        if not self.writer.isOpened():
            print(f"Warning: Failed to initialize video writer with {PRIMARY_CODEC} codec")
            print(f"Falling back to {FALLBACK_CODEC} codec...")
            self.writer = cv2.VideoWriter(
                self.output_path,
                cv2.VideoWriter_fourcc(*FALLBACK_CODEC),
                self.fps,
                (self.frame_width, self.frame_height)
            )
            
            if not self.writer.isOpened():
                raise ValueError("Could not initialize video writer with any codec")
    
    def process_video(self, frame_processor_func):
        """
        Process video frame by frame within the specified time range.
        
        Args:
            frame_processor_func: Function that processes each frame
                                 Should accept (frame, frame_number) and return processed_frame
        """
        if not self.cap or not self.writer:
            raise ValueError("Video processor not initialized. Call initialize() first.")
        
        print(f"\nStarting video processing...")
        print(f"Processing frames: {self.start_frame} to {self.end_frame} ({self.processing_frames} frames)")
        
        # Seek to start frame
        if self.start_frame > 0:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
            print(f"Seeking to frame {self.start_frame}...")
        
        frame_number = self.start_frame
        processed_count = 0
        start_time = time.time()
        
        while self.cap.isOpened() and frame_number < self.end_frame:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Process frame
            processed_frame = frame_processor_func(frame, frame_number)
            self.writer.write(processed_frame)
            
            # Progress reporting
            if processed_count % PROGRESS_UPDATE_INTERVAL == 0:
                self._report_progress(processed_count, start_time)
            
            frame_number += 1
            processed_count += 1
        
        # Final progress report
        elapsed_time = time.time() - start_time
        print(f"\n\nVideo processing completed in {elapsed_time:.1f} seconds")
        print(f"Processed {processed_count} frames at average {processed_count/elapsed_time:.1f} fps")
        
        if processed_count < self.processing_frames:
            print(f"Warning: Only processed {processed_count} of {self.processing_frames} expected frames")
    
    def _report_progress(self, processed_count, start_time):
        """Report processing progress."""
        elapsed_time = time.time() - start_time
        progress = (processed_count / self.processing_frames) * 100 if self.processing_frames > 0 else 0
        frames_per_second = processed_count / elapsed_time if elapsed_time > 0 else 0
        print(f"\rProcessing frame {processed_count}/{self.processing_frames} ({progress:.1f}%) - {frames_per_second:.1f} fps", end="")
    
    def cleanup(self):
        """Release video resources."""
        if self.cap:
            self.cap.release()
        if self.writer:
            self.writer.release()
        print(f"\nVideo saved to: {self.output_path}")
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
    
    @staticmethod
    def validate_input_files(video_path, model_path):
        """
        Validate that input files exist.
        
        Args:
            video_path: Path to input video
            model_path: Path to YOLO model
            
        Returns:
            bool: True if all files exist
        """
        if not Path(video_path).exists():
            print(f"Error: Video file not found: {video_path}")
            return False
        
        if not Path(model_path).exists():
            print(f"Error: YOLO model file not found: {model_path}")
            return False
        
        return True
