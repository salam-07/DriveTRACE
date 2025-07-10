import cv2
import numpy as np
from ultralytics import YOLO
import csv
from pathlib import Path
import supervision as sv
from collections import defaultdict
import time

class VehicleTracker:
    def __init__(self, video_path, model_path, output_video_path, output_csv_path):
        self.video_path = video_path
        self.output_video_path = output_video_path
        self.output_csv_path = output_csv_path
        
        # Initialize YOLO model
        self.model = YOLO(model_path)
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(video_path)
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        
        # Initialize video writer with a more compatible codec
        self.writer = cv2.VideoWriter(
            output_video_path,
            cv2.VideoWriter_fourcc(*'avc1'),  # H.264 codec
            self.fps,
            (self.frame_width, self.frame_height)
        )
        
        if not self.writer.isOpened():
            print("Warning: Failed to initialize video writer with avc1 codec")
            print("Falling back to mp4v codec...")
            self.writer = cv2.VideoWriter(
                output_video_path,
                cv2.VideoWriter_fourcc(*'mp4v'),
                self.fps,
                (self.frame_width, self.frame_height)
            )
        
        # Initialize tracker with frame rate
        self.tracker = sv.ByteTrack(frame_rate=self.fps)
        
        # Initialize annotators
        self.box_annotator = sv.BoxAnnotator(thickness=2)
        self.trace_annotator = sv.TraceAnnotator(thickness=2, trace_length=75)
        
        # Get class names from model
        self.class_names = self.model.model.names
        
        # Store vehicle data
        self.vehicle_data = defaultdict(lambda: {
            'positions': [],
            'speeds': [],
            'frames': [],
            'initial_position': None
        })
        
        # Define ROI points (replace these with your actual points)
        self.roi_points = np.array([
            [int(self.frame_width * 0.2), int(self.frame_height * 0.2)],
            [int(self.frame_width * 0.8), int(self.frame_height * 0.2)],
            [int(self.frame_width * 0.8), int(self.frame_height * 0.8)],
            [int(self.frame_width * 0.2), int(self.frame_height * 0.8)]
        ], dtype=np.float32)
        
        # Define destination points for perspective transform
        self.dst_points = np.array([
            [0, 0],
            [400, 0],
            [400, 600],
            [0, 600]
        ], dtype=np.float32)
        
        # Calculate perspective transform matrix
        self.perspective_matrix = cv2.getPerspectiveTransform(self.roi_points, self.dst_points)

    def point_in_roi(self, point):
        return cv2.pointPolygonTest(self.roi_points.astype(np.int32), tuple(point), False) >= 0

    def process_frame(self, frame, frame_number):
        # Draw ROI
        cv2.polylines(frame, [self.roi_points.astype(np.int32)], True, (0, 255, 0), 2)
        
        # Run YOLO detection
        results = self.model(frame, verbose=False)[0]
        detections = sv.Detections.from_ultralytics(results)
        
        # Filter detections for vehicles only
        mask = np.array([class_id in [2, 3, 5, 7] for class_id in detections.class_id])  # cars, trucks, buses, etc.
        detections = detections[mask]
        
        if len(detections) == 0:
            return frame  # Return the frame if no vehicles detected
        
        # Update tracks
        detections = self.tracker.update_with_detections(detections)
        
        # Process each tracked vehicle
        calculate_speed = frame_number % 5 == 0  # Calculate speed every 5th frame
        for confidence, class_id, tracker_id, box in zip(detections.confidence, detections.class_id, detections.tracker_id, detections.xyxy):
            # Get center point of bounding box
            x1, y1, x2, y2 = box.astype(int)
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            center_point = np.array([center_x, center_y])
            
            if self.point_in_roi(center_point):
                    # Transform point to bird's eye view
                    transformed_point = cv2.perspectiveTransform(
                        np.array([[center_point]], dtype=np.float32),
                        self.perspective_matrix
                    )[0][0]
                    
                    # Store data
                    if self.vehicle_data[tracker_id]['initial_position'] is None:
                        self.vehicle_data[tracker_id]['initial_position'] = transformed_point
                    
                    self.vehicle_data[tracker_id]['positions'].append(transformed_point)
                    self.vehicle_data[tracker_id]['frames'].append(frame_number)
                    
                    # Store data for every frame
                    self.vehicle_data[tracker_id]['positions'].append(transformed_point)
                    self.vehicle_data[tracker_id]['frames'].append(frame_number)
                    
                    # Initialize speed
                    speed = 0 if not self.vehicle_data[tracker_id]['speeds'] else self.vehicle_data[tracker_id]['speeds'][-1]
                    
                    # Calculate speed every 5th frame if we have at least two positions
                    if calculate_speed and len(self.vehicle_data[tracker_id]['positions']) >= 2:
                        pos1 = self.vehicle_data[tracker_id]['positions'][-2]
                        pos2 = self.vehicle_data[tracker_id]['positions'][-1]
                        time_diff = (self.vehicle_data[tracker_id]['frames'][-1] - 
                                   self.vehicle_data[tracker_id]['frames'][-2]) / self.fps
                        
                        # Calculate speed in pixels per second
                        distance = np.linalg.norm(pos2 - pos1)
                        speed = distance / time_diff if time_diff > 0 else 0
                        self.vehicle_data[tracker_id]['speeds'].append(speed)
                    
                    # Draw bounding box and ID
                    label = f"{tracker_id} {self.class_names[class_id]} {confidence:0.2f} Speed: {speed:.1f}px/s"
                    cv2.rectangle(frame, 
                                (x1, y1), 
                                (x2, y2), 
                                (0, 255, 0), 2)
                    cv2.putText(frame, label, 
                              (x1, y1 - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Update trace annotator
        frame = self.trace_annotator.annotate(scene=frame.copy(), detections=detections)
        
        # Update box annotator
        frame = self.box_annotator.annotate(scene=frame, detections=detections)
        
        return frame

    def save_to_csv(self):
        print(f"\nProcessing vehicle tracking data...")
        with open(self.output_csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['frame', 'vehicle_id', 'x_position', 'y_position', 
                           'spawn_x', 'spawn_y', 'relative_x', 'relative_y', 
                           'speed_px_per_s'])
            total_vehicles = len(self.vehicle_data)
            print(f"Processing data for {total_vehicles} vehicles...")
            
            for vehicle_id, data in self.vehicle_data.items():
                if data['initial_position'] is not None:
                    for i in range(len(data['positions'])):
                        pos = data['positions'][i]
                        init_pos = data['initial_position']
                        relative_pos = pos - init_pos
                        speed = data['speeds'][i] if i < len(data['speeds']) else 0
                        
                        writer.writerow([
                            data['frames'][i],
                            vehicle_id,
                            pos[0],
                            pos[1],
                            init_pos[0],
                            init_pos[1],
                            relative_pos[0],
                            relative_pos[1],
                            speed
                        ])

    def process_video(self):
        frame_number = 0
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"\nStarting video processing...")
        print(f"Total frames to process: {total_frames}")
        
        start_time = time.time()
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            
            processed_frame = self.process_frame(frame, frame_number)
            self.writer.write(processed_frame)
            
            # Progress reporting
            if frame_number % 30 == 0:  # Update progress every 30 frames
                elapsed_time = time.time() - start_time
                progress = (frame_number / total_frames) * 100
                frames_per_second = frame_number / elapsed_time if elapsed_time > 0 else 0
                print(f"\rProcessing frame {frame_number}/{total_frames} ({progress:.1f}%) - {frames_per_second:.1f} fps", end="")
            
            frame_number += 1
            
        elapsed_time = time.time() - start_time
        print(f"\n\nVideo processing completed in {elapsed_time:.1f} seconds")
        print(f"Processed {frame_number} frames at average {frame_number/elapsed_time:.1f} fps")
        
        self.cap.release()
        self.writer.release()
        print("Saving tracking data to CSV...")
        self.save_to_csv()
        print(f"Data saved to: {self.output_csv_path}")

def main():
    video_path = "Detection/test2.mp4"
    model_path = "Detection/yolov8m.pt"  # Using medium-sized YOLOv8 model
    output_video_path = "Detection/annotated_test2.mp4"
    output_csv_path = "Detection/vehicle_data.csv"
    
    # Check if input files exist
    if not Path(video_path).exists():
        print(f"Error: Video file not found: {video_path}")
        return
    if not Path(model_path).exists():
        print(f"Error: YOLO model file not found: {model_path}")
        return
    
    print(f"Starting vehicle detection and tracking...")
    print(f"Input video: {video_path}")
    print(f"Using YOLO model: {model_path}")
    
    tracker = VehicleTracker(video_path, model_path, output_video_path, output_csv_path)
    tracker.process_video()

if __name__ == "__main__":
    main()
