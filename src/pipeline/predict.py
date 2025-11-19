import pandas as pd
import xgboost as xgb
import pickle
import os
import numpy as np

class F1Predictor:
    def __init__(self, model_path, features_path):
        self.model_path = model_path
        self.features_path = features_path
        self.model = None
        self.history_df = None
        self.load_resources()

    def load_resources(self):
        """Loads model and historical data."""
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
        else:
            raise FileNotFoundError(f"Model not found at {self.model_path}")
            
        if os.path.exists(self.features_path):
            self.history_df = pd.read_csv(self.features_path)
        else:
            raise FileNotFoundError(f"Features not found at {self.features_path}")

    def preprocess_input(self, race_input):
        """
        Preprocesses input data for a new race.
        race_input: List of dicts (one per driver) with keys:
            - driverId
            - constructorId
            - grid
            - Location
        """
        # Convert input to DataFrame
        input_df = pd.DataFrame(race_input)
        
        # We need to calculate derived features:
        # driver_win_rate, driver_recent_form, constructor_win_rate, constructor_recent_points
        # We will look up these values from the latest history for each driver/constructor.
        
        # Get latest stats from history
        # This is a simplification. Ideally we re-calculate rolling windows including the new race?
        # No, we use stats UP TO this race.
        
        # Create lookup dicts
        # We take the last known value for each driver/constructor
        # Sort history by year/round
        # Assuming history_df is sorted or we sort it
        # Actually, we can just take the mean of the last 3 races from history for "recent form"
        # and cumulative stats from the last record.
        
        # For simplicity, we will just take the last record for each driver in history
        last_driver_stats = self.history_df.sort_values('year').groupby('driverId').last()
        last_constructor_stats = self.history_df.sort_values('year').groupby('constructorId').last()
        
        # Map stats to input
        input_df['driver_win_rate'] = input_df['driverId'].map(last_driver_stats['driver_win_rate']).fillna(0)
        input_df['driver_recent_form'] = input_df['driverId'].map(last_driver_stats['driver_recent_form']).fillna(20)
        
        input_df['constructor_win_rate'] = input_df['constructorId'].map(last_constructor_stats['constructor_win_rate']).fillna(0)
        input_df['constructor_recent_points'] = input_df['constructorId'].map(last_constructor_stats['constructor_recent_points']).fillna(0)
        
        # Encode Categoricals
        # We need to use the same encoding as training.
        # Since we used .cat.codes, we need to map the categories.
        # Ideally we should have saved the encoders.
        # For now, we will try to map based on the history_df codes.
        
        # Create mappings
        loc_map = dict(zip(self.history_df['Location'], self.history_df['location_id']))
        driver_map = dict(zip(self.history_df['driverId'], self.history_df['driver_id_enc']))
        const_map = dict(zip(self.history_df['constructorId'], self.history_df['constructor_id_enc']))
        
        input_df['location_id'] = input_df['Location'].map(loc_map).fillna(-1)
        input_df['driver_id_enc'] = input_df['driverId'].map(driver_map).fillna(-1)
        input_df['constructor_id_enc'] = input_df['constructorId'].map(const_map).fillna(-1)
        
        # Select features
        features = [
            'grid', 'driver_win_rate', 'driver_recent_form',
            'constructor_win_rate', 'constructor_recent_points',
            'location_id', 'driver_id_enc', 'constructor_id_enc'
        ]
        
        return input_df[features]

    def predict(self, race_input):
        """Generates predictions."""
        X = self.preprocess_input(race_input)
        
        # Predict
        probs = self.model.predict_proba(X)[:, 1]
        
        # Format output
        results = []
        for i, prob in enumerate(probs):
            results.append({
                'driverId': race_input[i]['driverId'],
                'win_probability': float(prob)
            })
            
        # Sort by probability
        results.sort(key=lambda x: x['win_probability'], reverse=True)
        return results

    def get_drivers(self):
        """Returns list of unique drivers."""
        return sorted(self.history_df['driverId'].unique().tolist())

    def get_constructors(self):
        """Returns list of unique constructors."""
        return sorted(self.history_df['constructorId'].unique().tolist())

    def get_locations(self):
        """Returns list of unique locations."""
        return sorted(self.history_df['Location'].unique().tolist())

if __name__ == "__main__":
    # Test run
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    model_path = os.path.join(base_dir, "src", "models", "xgb_winner_model.pkl")
    features_path = os.path.join(base_dir, "data", "features", "final_features.csv")
    
    predictor = F1Predictor(model_path, features_path)
    
    # Mock input for a 2026 race
    mock_input = [
        {'driverId': 'max_verstappen', 'constructorId': 'red_bull', 'grid': 1, 'Location': 'Monza'},
        {'driverId': 'leclerc', 'constructorId': 'ferrari', 'grid': 2, 'Location': 'Monza'},
        {'driverId': 'hamilton', 'constructorId': 'ferrari', 'grid': 3, 'Location': 'Monza'}, # Hamilton at Ferrari in 2025/26!
        {'driverId': 'norris', 'constructorId': 'mclaren', 'grid': 4, 'Location': 'Monza'},
    ]
    
    predictions = predictor.predict(mock_input)
    print("Predicted Winner Probabilities:")
    for p in predictions:
        print(f"{p['driverId']}: {p['win_probability']:.4f}")
