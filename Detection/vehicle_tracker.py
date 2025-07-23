"""
Main vehicle tracker class that coordinates all detection modules.
"""

import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv
from collections import defaultdict

from detection_config import *
from speed_calculator import SpeedCalculator
from coordinate_transformer import CoordinateTransformer
from csv_exporter import CSVExporter
from video_processor import VideoProcessor

class VehicleTracker:
    def __init__(self, video_path, model_path, output_video_path, output_csv_path, 
                 start_time=None, end_time=None):
        self.video_path = video_path
        self.model_path = model_path
        self.output_video_path = output_video_path
        self.output_csv_path = output_csv_path
        self.start_time = start_time
        self.end_time = end_time
        
        # Initialize components
        self.model = None
        self.tracker = None
        self.speed_calculator = None
        self.coordinate_transformer = None
        self.csv_exporter = None
        self.video_processor = None
        
        # Initialize annotators
        self.box_annotator = None
        self.trace_annotator = None
        
        # Vehicle tracking data
        self.vehicle_data = defaultdict(lambda: {
            'positions': [],
            'speeds': [],
            'frames': [],
            'initial_position': None
        })
        
        # Model class names
        self.class_names = {}
    
    def initialize(self):
        """Initialize all components."""
        print("Initializing vehicle tracker...")
        
        # Validate input files
        if not VideoProcessor.validate_input_files(self.video_path, self.model_path):
            raise ValueError("Input file validation failed")
        
        # Initialize YOLO model
        print("Loading YOLO model...")
        self.model = YOLO(self.model_path)
        self.class_names = self.model.model.names
        
        # Initialize video processor
        self.video_processor = VideoProcessor(
            self.video_path, 
            self.output_video_path,
            start_time=self.start_time,
            end_time=self.end_time
        )
        self.video_processor.initialize()
        
        # Initialize coordinate transformer
        self.coordinate_transformer = CoordinateTransformer(
            self.video_processor.frame_width,
            self.video_processor.frame_height
        )
        
        # Initialize speed calculator
        self.speed_calculator = SpeedCalculator(self.video_processor.fps)
        
        # Initialize tracker
        self.tracker = sv.ByteTrack(frame_rate=self.video_processor.fps)
        
        # Initialize annotators
        self.box_annotator = sv.BoxAnnotator(thickness=BOX_THICKNESS)
        self.trace_annotator = sv.TraceAnnotator(
            thickness=BOX_THICKNESS, 
            trace_length=TRACE_LENGTH
        )
        
        # Initialize CSV exporter
        self.csv_exporter = CSVExporter(self.output_csv_path)
        self.csv_exporter.set_coordinate_transformer(self.coordinate_transformer)
        
        print("Vehicle tracker initialized successfully!")
    
    def process_frame(self, frame, frame_number):
        """
        Process a single frame for vehicle detection and tracking.
        
        Args:
            frame: Input video frame
            frame_number: Current frame number
            
        Returns:
            Processed frame with annotations
        """
        # Draw ROI
        frame = self.coordinate_transformer.draw_roi(frame)
        
        # Run YOLO detection
        results = self.model(frame, verbose=False)[0]
        detections = sv.Detections.from_ultralytics(results)
        
        # Filter detections for vehicles only
        mask = np.array([
            class_id in VEHICLE_CLASS_IDS 
            for class_id in detections.class_id
        ])
        detections = detections[mask]
        
        if len(detections) == 0:
            return frame  # Return the frame if no vehicles detected
        
        # Update tracks
        detections = self.tracker.update_with_detections(detections)
        
        # Process each tracked vehicle
        for confidence, class_id, tracker_id, box in zip(
            detections.confidence, 
            detections.class_id, 
            detections.tracker_id, 
            detections.xyxy
        ):
            self._process_vehicle(box, tracker_id, class_id, frame_number, frame)
        
        # Apply annotations
        frame = self.trace_annotator.annotate(scene=frame.copy(), detections=detections)
        frame = self.box_annotator.annotate(scene=frame, detections=detections)
        
        return frame
    
    def _process_vehicle(self, box, tracker_id, class_id, frame_number, frame):
        """Process a single tracked vehicle."""
        # Get center point of bounding box
        x1, y1, x2, y2 = box.astype(int)
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        center_point = np.array([center_x, center_y])
        
        # Check if vehicle is in ROI
        if not self.coordinate_transformer.point_in_roi(center_point):
            return
        
        # Transform point to bird's eye view
        transformed_point = self.coordinate_transformer.transform_to_birds_eye(center_point)
        
        # Store initial position
        if self.vehicle_data[tracker_id]['initial_position'] is None:
            self.vehicle_data[tracker_id]['initial_position'] = transformed_point
        
        # Store tracking data
        self.vehicle_data[tracker_id]['positions'].append(transformed_point)
        self.vehicle_data[tracker_id]['frames'].append(frame_number)
        
        # Calculate speeds
        speed_display, speed_simulation = self.speed_calculator.calculate_speeds(
            self.vehicle_data[tracker_id]['positions'],
            self.vehicle_data[tracker_id]['frames']
        )
        
        self.vehicle_data[tracker_id]['speeds'].append(speed_simulation)
        
        # Draw annotation
        self._draw_vehicle_annotation(frame, x1, y1, tracker_id, class_id, speed_display)
    
    def _draw_vehicle_annotation(self, frame, x1, y1, tracker_id, class_id, speed_display):
        """Draw vehicle annotation on frame."""
        label = f"ID:{tracker_id} {self.class_names[class_id]} Speed:{speed_display}px/s"
        cv2.putText(
            frame, 
            label, 
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 
            FONT_SCALE, 
            (255, 255, 255), 
            FONT_THICKNESS
        )
    
    def process_video(self):
        """Process the entire video."""
        print(f"Starting vehicle detection and tracking for simulation data...")
        print(f"Input video: {self.video_path}")
        print(f"Using YOLO model: {self.model_path}")
        print(f"Output CSV format: frame_id,vehicle_id,world_x,world_y,speed,action")
        
        # Process video
        with self.video_processor:
            self.video_processor.process_video(self.process_frame)
        
        # Export CSV data
        print("Saving tracking data to CSV...")
        if self.csv_exporter.validate_data(self.vehicle_data):
            self.csv_exporter.export_vehicle_data(self.vehicle_data)
        else:
            print("No valid tracking data to export")
    
    def run(self):
        """Run the complete vehicle tracking pipeline."""
        try:
            self.initialize()
            self.process_video()
            print("Vehicle tracking completed successfully!")
        except Exception as e:
            print(f"Error during vehicle tracking: {e}")
            raise
