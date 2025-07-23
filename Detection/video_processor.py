"""
Video processing utilities for vehicle detection and annotation.
"""

import cv2
import time
from pathlib import Path
from detection_config import *

class VideoProcessor:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.cap = None
        self.writer = None
        self.frame_width = 0
        self.frame_height = 0
        self.fps = 0
        self.total_frames = 0
    
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
        
        # Initialize video writer
        self._initialize_writer()
        
        print(f"Video initialized:")
        print(f"  Resolution: {self.frame_width}x{self.frame_height}")
        print(f"  FPS: {self.fps}")
        print(f"  Total frames: {self.total_frames}")
    
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
        Process video frame by frame.
        
        Args:
            frame_processor_func: Function that processes each frame
                                 Should accept (frame, frame_number) and return processed_frame
        """
        if not self.cap or not self.writer:
            raise ValueError("Video processor not initialized. Call initialize() first.")
        
        frame_number = 0
        start_time = time.time()
        
        print(f"\nStarting video processing...")
        print(f"Total frames to process: {self.total_frames}")
        
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Process frame
            processed_frame = frame_processor_func(frame, frame_number)
            self.writer.write(processed_frame)
            
            # Progress reporting
            if frame_number % PROGRESS_UPDATE_INTERVAL == 0:
                self._report_progress(frame_number, start_time)
            
            frame_number += 1
        
        # Final progress report
        elapsed_time = time.time() - start_time
        print(f"\n\nVideo processing completed in {elapsed_time:.1f} seconds")
        print(f"Processed {frame_number} frames at average {frame_number/elapsed_time:.1f} fps")
    
    def _report_progress(self, frame_number, start_time):
        """Report processing progress."""
        elapsed_time = time.time() - start_time
        progress = (frame_number / self.total_frames) * 100
        frames_per_second = frame_number / elapsed_time if elapsed_time > 0 else 0
        print(f"\rProcessing frame {frame_number}/{self.total_frames} ({progress:.1f}%) - {frames_per_second:.1f} fps", end="")
    
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
