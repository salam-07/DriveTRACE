import csv
import os
from config import LANE_WIDTH

#import data from CSV
#not implemented

TRAFFIC_CSV_PATH = os.path.join('Assets', 'traffic_data.csv')

def load_traffic_data():
    """
    Loads traffic vehicle data from traffic_data.csv.
    Returns a list of dicts with keys: 'lane', 'world_y', 'speed'.
    """
    traffic_list = []
    with open(TRAFFIC_CSV_PATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Derive lane from x, world_y from y, speed from speed_px_per_s
            x = float(row['x'])
            y = float(row['y'])
            speed = float(row['speed_px_per_s'])
            lane = int(x // LANE_WIDTH)
            traffic_list.append({
                'lane': lane,
                'world_y': y,
                'speed': speed
            })
    return traffic_list

# Example usage:
if __name__ == "__main__":
    data = load_traffic_data()
    for entry in data:
        print(entry)
