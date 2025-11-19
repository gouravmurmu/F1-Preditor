import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report, log_loss
import os
import pickle

def load_features(features_dir):
    """Loads feature dataset."""
    path = os.path.join(features_dir, "final_features.csv")
    return pd.read_csv(path)

def train_model(df):
    """Trains XGBoost model for race winner prediction."""
    # Time-based split
    # We have 2023 and 2024 data.
    # Train on 2023, Test on 2024.
    
    train_df = df[df['year'] < 2024]
    test_df = df[df['year'] == 2024]
    
    print(f"Train set: {len(train_df)} rows")
    print(f"Test set: {len(test_df)} rows")
    
    features = [
        'grid', 'driver_win_rate', 'driver_recent_form',
        'constructor_win_rate', 'constructor_recent_points',
        'location_id', 'driver_id_enc', 'constructor_id_enc'
    ]
    target = 'is_winner'
    
    X_train = train_df[features]
    y_train = train_df[target]
    X_test = test_df[features]
    y_test = test_df[target]
    
    # XGBoost Classifier
    model = xgb.XGBClassifier(
        objective='binary:logistic',
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    
    print("Training model...")
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, preds)
    loss = log_loss(y_test, probs)
    
    print(f"Accuracy: {acc:.4f}")
    print(f"Log Loss: {loss:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, preds))
    
    return model

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    features_dir = os.path.join(base_dir, "data", "features")
    models_dir = os.path.join(base_dir, "src", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    df = load_features(features_dir)
    model = train_model(df)
    
    # Save model
    with open(os.path.join(models_dir, "xgb_winner_model.pkl"), "wb") as f:
        pickle.dump(model, f)
    print("Model saved.")
