import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

def generate_training_data():
    """
    Generate realistic training data based on
    known NER landslide patterns from research
    """
    np.random.seed(42)
    n = 2000

    data = []
    for _ in range(n):
        rainfall = np.random.uniform(0, 300)
        slope = np.random.uniform(5, 60)
        soil_moisture = np.random.uniform(0.1, 1.0)
        ground_displacement = np.random.uniform(0, 5)
        seismic = np.random.uniform(0, 1)
        erosion_class = np.random.randint(1, 6)
        historical_count = np.random.randint(0, 15)
        ndvi = np.random.uniform(0.1, 0.9)
        elevation = np.random.uniform(200, 3000)

        # Realistic landslide logic based on research
        risk = (
            (rainfall / 300) * 35 +
            (slope / 60) * 25 +
            soil_moisture * 15 +
            (ground_displacement / 5) * 12 +
            seismic * 8 +
            (erosion_class / 5) * 5
        )

        # Label — 1 = landslide occurred
        label = 1 if (
            risk > 55 or
            (rainfall > 150 and slope > 30) or
            (soil_moisture > 0.85 and slope > 25) or
            (ground_displacement > 3 and rainfall > 100)
        ) else 0

        data.append([
            rainfall, slope, soil_moisture,
            ground_displacement, seismic,
            erosion_class, historical_count,
            ndvi, elevation, label
        ])

    df = pd.DataFrame(data, columns=[
        'rainfall_24hr', 'slope_degrees', 'soil_moisture',
        'ground_displacement', 'seismic_activity',
        'erosion_class', 'historical_count',
        'ndvi', 'elevation', 'label'
    ])
    return df

def train_model():
    print("Generating training data...")
    df = generate_training_data()

    X = df.drop('label', axis=1)
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("Training XGBoost model...")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss'
    )
    model.fit(X_train, y_train)

    print("\nModel Performance:")
    print(classification_report(y_test, model.predict(X_test)))

    # Save model
    os.makedirs('ml', exist_ok=True)
    joblib.dump(model, 'ml/model.pkl')
    print("Model saved to ml/model.pkl")

if __name__ == "__main__":
    train_model()