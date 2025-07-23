"""
Coordinate transformation utilities for perspective correction and world coordinate mapping.
"""

import cv2
import numpy as np
from detection_config import *

class CoordinateTransformer:
    def __init__(self, frame_width, frame_height):
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Define ROI points based on frame dimensions
        self.roi_points = np.array([
            [int(frame_width * x), int(frame_height * y)]
            for x, y in ROI_RELATIVE_POINTS
        ], dtype=np.float32)
        
        # Define destination points for perspective transform
        self.dst_points = np.array(PERSPECTIVE_DST_POINTS, dtype=np.float32)
        
        # Calculate perspective transform matrix
        self.perspective_matrix = cv2.getPerspectiveTransform(
            self.roi_points, self.dst_points
        )
    
    def point_in_roi(self, point):
        """Check if a point is within the region of interest."""
        return cv2.pointPolygonTest(
            self.roi_points.astype(np.int32), 
            tuple(point), 
            False
        ) >= 0
    
    def transform_to_birds_eye(self, point):
        """Transform a point to bird's eye view coordinates."""
        return cv2.perspectiveTransform(
            np.array([[point]], dtype=np.float32),
            self.perspective_matrix
        )[0][0]
    
    def to_simulation_coordinates(self, bird_eye_point):
        """
        Convert bird's eye view coordinates to simulation world coordinates.
        
        Args:
            bird_eye_point: (x, y) point in bird's eye view
            
        Returns:
            tuple: (world_x, world_y) in simulation coordinates
        """
        # Map bird's eye view coordinates to lane-based system
        world_x = int(bird_eye_point[0] * 2)  # Scale to lane width
        world_y = int(bird_eye_point[1] * 5)  # Scale for forward movement
        return world_x, world_y
    
    def draw_roi(self, frame):
        """Draw the region of interest on the frame."""
        cv2.polylines(
            frame, 
            [self.roi_points.astype(np.int32)], 
            True, 
            (0, 255, 0), 
            2
        )
        return frame
