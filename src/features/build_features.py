import pandas as pd
import numpy as np
import os

def load_processed_data(processed_data_dir):
    """Loads processed race data."""
    path = os.path.join(processed_data_dir, "race_data.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        raise FileNotFoundError(f"{path} not found.")

def calculate_driver_metrics(df):
    """Calculates cumulative driver performance metrics."""
    # Sort by date
    df = df.sort_values(['year', 'round'])
    
    # Cumulative Wins
    df['driver_wins_cum'] = df.groupby('driverId')['is_winner'].cumsum() - df['is_winner']
    df['driver_races_cum'] = df.groupby('driverId').cumcount()
    df['driver_win_rate'] = df['driver_wins_cum'] / df['driver_races_cum'].replace(0, 1)
    
    # Recent Form (Avg position last 3 races)
    # We need to handle DNFs or use positionOrder
    # positionOrder is usually numeric, but might be string if DNF?
    # In FastF1, Position is float.
    
    df['position_numeric'] = pd.to_numeric(df['positionOrder'], errors='coerce').fillna(20) # Treat DNF as 20
    
    df['driver_recent_form'] = df.groupby('driverId')['position_numeric'].transform(
        lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
    )
    
    return df

def calculate_constructor_metrics(df):
    """Calculates cumulative constructor performance metrics."""
    df = df.sort_values(['year', 'round'])
    
    # Cumulative Wins
    df['constructor_wins_cum'] = df.groupby('constructorId')['is_winner'].cumsum() - df['is_winner']
    df['constructor_races_cum'] = df.groupby('constructorId').cumcount()
    df['constructor_win_rate'] = df['constructor_wins_cum'] / df['constructor_races_cum'].replace(0, 1)
    
    # Recent Form (Avg points last 3 races)
    df['constructor_recent_points'] = df.groupby('constructorId')['points'].transform(
        lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
    )
    
    return df

def encode_categorical(df):
    """Encodes categorical features."""
    # Label Encode Location/Circuit
    # For simplicity in this script, we'll use frequency encoding or just ID
    # But for a real model, we might want OneHot or Target Encoding.
    # Let's use Label Encoding for tree models.
    
    df['location_id'] = df['Location'].astype('category').cat.codes
    df['constructor_id_enc'] = df['constructorId'].astype('category').cat.codes
    df['driver_id_enc'] = df['driverId'].astype('category').cat.codes
    
    return df

def add_2026_regulation_dummy(df):
    """Adds a dummy feature for regulation changes."""
    # 2026 is not in data, but we add the column for future inference
    df['regulation_change'] = 0
    return df

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    processed_dir = os.path.join(base_dir, "data", "processed")
    features_dir = os.path.join(base_dir, "data", "features")
    os.makedirs(features_dir, exist_ok=True)
    
    print("Loading data...")
    df = load_processed_data(processed_dir)
    
    print("Calculating Driver Metrics...")
    df = calculate_driver_metrics(df)
    
    print("Calculating Constructor Metrics...")
    df = calculate_constructor_metrics(df)
    
    print("Encoding Features...")
    df = encode_categorical(df)
    
    print("Adding Regulation Features...")
    df = add_2026_regulation_dummy(df)
    
    # Fill NaNs
    df = df.fillna(0)
    
    # Save feature set
    output_path = os.path.join(features_dir, "final_features.csv")
    df.to_csv(output_path, index=False)
    print(f"Saved features to {output_path} with {len(df)} rows.")
