import csv
import os

TRAFFIC_CSV_PATH = os.path.join('Assets', 'traffic_data.csv')

def load_traffic_data():
    """
    Loads traffic vehicle data from traffic_data.csv.
    Returns a list of dicts with keys: 'lane', 'world_y', 'speed'.
    """
    traffic_list = []
    with open(TRAFFIC_CSV_PATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        print('CSV fieldnames:', reader.fieldnames)  # Debug print
        for row in reader:
            try:
                traffic_list.append({
                    'lane': int(row['lane']),
                    'world_y': float(row['world_y']),
                    'speed': float(row['speed'])
                })
            except KeyError as e:
                print('Row keys:', row.keys())
                raise
    return traffic_list

# Example usage:
if __name__ == "__main__":
    data = load_traffic_data()
    for entry in data:
        print(entry)
