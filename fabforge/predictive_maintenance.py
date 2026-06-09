import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import json
import time

class PredictiveMaintenance:
    def __init__(self):
        self.model = None
        self.data = []
    
    def generate_synthetic_data(self, n_samples=1000):
        np.random.seed(42)
        data = pd.DataFrame({
            'temp': np.random.normal(200, 20, n_samples),
            'vibration': np.random.normal(0.5, 0.1, n_samples),
            'pressure': np.random.normal(0.01, 0.005, n_samples),
            'runtime': np.random.randint(100, 10000, n_samples),
            'failure': np.random.binomial(1, 0.1, n_samples)
        })
        return data
    
    def train(self):
        data = self.generate_synthetic_data()
        X = data.drop('failure', axis=1)
        y = data['failure']
        self.model = RandomForestRegressor(n_estimators=100)
        self.model.fit(X, y)
        joblib.dump(self.model, 'models/predictive_model.pkl')
        print("Predictive Maintenance model trained!")
    
    def predict(self, sensor_data):
        if self.model is None:
            self.model = joblib.load('models/predictive_model.pkl')
        df = pd.DataFrame([sensor_data])
        prob = self.model.predict(df)[0]
        alert = prob > 0.7
        return {"failure_prob": float(prob), "alert": alert}

pm = PredictiveMaintenance()
if __name__ == "__main__":
    pm.train()
