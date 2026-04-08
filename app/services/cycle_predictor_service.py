import joblib
import numpy as np
from datetime import timedelta

class CyclePredictor:

    def __init__(self, model_path: str):
        self.model = joblib.load(model_path)

    def predict_length(self, last_cycle, rolling_mean, rolling_std):
        X = np.array([[last_cycle, rolling_mean, rolling_std]])
        prediction = self.model.predict(X)[0]
        return round(prediction, 2)

    def predict_next_date(self, last_period_start, predicted_length):
        return last_period_start + timedelta(days=int(predicted_length))

    def predict_with_range(self, cycles, last_period_date):

        # Filtrar ciclos válidos (experimental)
        # cycle_lengths = [c for c in cycles if 15 <= c <= 45]

        cycle_lengths = cycles
        if len(cycle_lengths) < 3:
            raise ValueError("Not enough data to make a prediction")

        # Features
        last_cycle = cycle_lengths[-1]
        rolling_mean = np.mean(cycle_lengths[-3:])
        rolling_std = np.std(cycle_lengths[-3:])

        # Predicción usando el modelo
        X = np.array([[last_cycle, rolling_mean, rolling_std]])
        predicted_length = self.model.predict(X)[0]

        # Variabilidad (usa todos los ciclos, no solo 3)
        std = np.std(cycle_lengths)

        lower = predicted_length - std
        upper = predicted_length + std

        # Fechas
        predicted_date = last_period_date + timedelta(days=int(predicted_length))
        earliest_date = last_period_date + timedelta(days=int(lower))
        latest_date = last_period_date + timedelta(days=int(upper))

        return {
            "predicted_length": round(predicted_length, 2),
            "predicted_next_period": predicted_date,
            "earliest_expected_date": earliest_date,
            "latest_expected_date": latest_date
        }