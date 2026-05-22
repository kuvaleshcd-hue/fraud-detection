from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

# Initialize FastAPI
app = FastAPI()

# Load trained model
model = joblib.load("model.pkl")

# Request schema
class Transaction(BaseModel):
    amount: float
    location: int
    merchant: int
    device: int

# Home route
@app.get("/")
def home():
    return {"message": "Fraud Detection API Running"}

# Prediction route
@app.post("/predict")
def predict(transaction: Transaction):

    data = np.array([[
        transaction.amount,
        transaction.location,
        transaction.merchant,
        transaction.device
    ]])

    prediction = model.predict(data)[0]
    probability = model.predict_proba(data)[0][1]

    return {
        "fraud_prediction": int(prediction),
        "fraud_probability": float(probability)
    }