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