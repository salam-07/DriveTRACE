#for traffic speeds and behavior control
import os
# Game configuration settings

# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Road settings
ROAD_TILE_WIDTH = 800  # Width of road tile
ROAD_TILE_HEIGHT = 800  # Height of road tile
LANE_COUNT = 4
LANE_WIDTH = ROAD_TILE_WIDTH / LANE_COUNT

# Vehicle settings
VEHICLE_SCALE = 0.55  # Scale factor for vehicle sprites
MAX_SPEED = 300  # pixels per second
MIN_SPEED = 0
ACCELERATION_RATE = 70  # pixels per second squared
TURNING_SPEED = 5  # degrees per frame
TURNING_ANGLE = 7  # degrees per frame for player vehicle

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Asset paths
PLAYER_CHOICE = 13
ROAD_CHOICE = 1
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'Assets')
ROAD_ASSET_DIR = os.path.join(ASSETS_DIR, 'roads', f'road_tile_{ROAD_CHOICE}.jpeg')
PLAYER_TILE_ASSET = os.path.join(ASSETS_DIR, 'vehicles', f'car_{PLAYER_CHOICE}.png')
TRAFFIC_ASSET_DIR = os.path.join(ASSETS_DIR, 'vehicles')

# Traffic settings
TRAFFIC_DENSITY = 40  # Number of vehicles per lane
TRAFFIC_SPEED_RANGE = (250, 400)  # Min and max speed for traffic vehicles