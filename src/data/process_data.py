import pandas as pd
import os
import numpy as np

def load_data(raw_data_dir):
    """Loads raw CSV files into DataFrames."""
    files = ["races.csv", "results.csv"]
    data = {}
    for file in files:
        path = os.path.join(raw_data_dir, file)
        if os.path.exists(path):
            print(f"Loading {file}...")
            data[file.replace(".csv", "")] = pd.read_csv(path)
        else:
            print(f"Warning: {file} not found.")
    return data

def process_data(data):
    """Merges and cleans FastF1 data."""
    if 'results' not in data or 'races' not in data:
        print("Missing results or races data.")
        return None

    results = data['results']
    races = data['races']
    
    # Ensure raceId is present and consistent
    # In fetch_fastf1.py, we added raceId to results.
    
    # Merge results with races
    # races.csv from fastf1 has 'RoundNumber', 'EventName', 'EventDate', 'year'
    # We need to create a matching raceId in races if not present, or merge on year/round
    
    races['raceId'] = races['year'].astype(str) + "_" + races['RoundNumber'].astype(str)
    
    # Merge
    df = pd.merge(results, races[['raceId', 'EventName', 'EventDate', 'Location']], on='raceId', how='left')
    
    # Rename columns to match standard ML features
    df.rename(columns={
        'DriverId': 'driverId',
        'TeamName': 'constructorId', # Using Name as ID for now
        'GridPosition': 'grid',
        'Position': 'positionOrder',
        'Points': 'points',
        'Status': 'status',
        'Time': 'time_str'
    }, inplace=True)
    
    # Create Winner Target
    df['is_winner'] = df['positionOrder'].apply(lambda x: 1 if x == 1.0 else 0)
    
    # Convert Time to milliseconds (if possible)
    # FastF1 Time is usually a Timedelta string or object.
    # We might need to parse it.
    
    # Filter columns
    cols = [
        'raceId', 'year', 'round', 'driverId', 'constructorId', 'grid', 
        'positionOrder', 'points', 'status', 'is_winner', 'EventName', 
        'Location', 'Abbreviation'
    ]
    # Keep existing columns
    cols = [c for c in cols if c in df.columns]
    
    return df[cols]

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    raw_dir = os.path.join(base_dir, "data", "raw")
    processed_dir = os.path.join(base_dir, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    data = load_data(raw_dir)
    
    if data:
        print("Processing Data...")
        df = process_data(data)
        if df is not None:
            df.to_csv(os.path.join(processed_dir, "race_data.csv"), index=False)
            print(f"Saved race_data.csv with {len(df)} rows.")
