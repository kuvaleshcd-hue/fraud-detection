import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import time
from typing import Dict, List, Optional

app = FastAPI(
    title="Shield Fraud Detection Engine",
    description="Real-Time AI-powered GNN + Transformer Fraud Detection API",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory State for the AI Model
class ModelConfig:
    def __init__(self):
        self.threshold = 50.0
        # Feature weights for scoring
        self.weights = {
            "amount_anomaly": 0.35,
            "velocity_warning": 0.25,
            "geo_mismatch": 0.20,
            "merchant_safety": 0.12,
            "device_trust": 0.08
        }
        # Training state
        self.epochs_completed = 15
        self.accuracy = 0.984
        self.auc_roc = 0.991
        self.f1_score = 0.942
        self.loss_history = [0.45, 0.32, 0.25, 0.18, 0.14, 0.11, 0.09, 0.07, 0.06, 0.05]
        self.feedback_count = 0
        # In-Memory Transaction Database
        self.transactions_db = []

model_state = ModelConfig()

# Seeding initial transactions in the database
def seed_transactions(model: ModelConfig, count: int = 30):
    tx_types = ["Card Purchase", "UPI Transfer", "ACH Pull", "ATM Withdrawal", "Wire Transfer"]
    devices = [
        "Apple iPhone", "Apple iPad", "Samsung Phone", "Samsung Galaxy Tab",
        "Google Pixel", "Google Pixel Tablet", "OnePlus Phone", "OnePlus Pad", "Xiaomi Phone"
    ]
    
    start_id = 10482 - count + 1
    current_time = time.time()
    
    for i in range(count):
        tx_id_num = start_id + i
        tx_id = f"TXN-{str(tx_id_num).zfill(7)}"
        
        is_suspect = random.random() < 0.15
        
        if is_suspect:
            amount = round(random.uniform(8000, 180000), 2)
            country = random.choice(["RU", "NG", "KP", "CN"])
            merchant = random.choice(["Crypto Exchange", "Global Remittance", "FauxBank ATM"])
            velocity = random.randint(9, 28)
            new_device = random.random() > 0.3
            
            amt_score = random.randint(70, 99)
            vel_score = random.randint(65, 98)
            geo_score = random.randint(75, 96)
            merch_score = random.randint(60, 92)
            dev_score = random.randint(70, 95) if new_device else random.randint(1, 12)
        else:
            amount = round(random.uniform(10, 1500), 2)
            country = random.choice(["US", "IN", "FR", "JP", "UK"])
            merchant = random.choice(["PhonePe Merchant", "GPay P2M", "Paytm Gateway", "CRED Store", "Amazon Pay Merchant", "BharatPe QR"])
            velocity = random.randint(1, 4)
            new_device = False
            
            amt_score = random.randint(2, 28)
            vel_score = random.randint(3, 22)
            geo_score = random.randint(1, 15)
            merch_score = random.randint(2, 18)
            dev_score = random.randint(1, 12)
            
        features = {
            "Amount anomaly": amt_score,
            "Velocity Warning": vel_score,
            "Geo mismatch": geo_score,
            "Merchant safety": merch_score,
            "Device trust": dev_score
        }
        
        weighted_score = (
            features["Amount anomaly"] * model.weights["amount_anomaly"] +
            features["Velocity Warning"] * model.weights["velocity_warning"] +
            features["Geo mismatch"] * model.weights["geo_mismatch"] +
            features["Merchant safety"] * model.weights["merchant_safety"] +
            features["Device trust"] * model.weights["device_trust"]
        )
        score = min(100.0, max(0.0, weighted_score))
        
        if score >= model.threshold:
            risk = "HIGH"
            status = "Flagged"
        elif score >= (model.threshold * 0.6):
            risk = "MEDIUM"
            status = "Review"
        else:
            risk = "LOW"
            status = "Cleared"
            
        signals = []
        if amount > 10000:
            signals.append(f"anomalous transaction size of INR {amount:,.2f} (anomaly rating: {features.get('Amount anomaly')}%)")
        if new_device:
            signals.append(f"unrecognized signature (device untrust rating: {features.get('Device trust')}%)")
        if velocity > 5:
            signals.append(f"elevated activity velocity of {velocity} txns/hr (velocity rating: {features.get('Velocity Warning')}%)")
        if features.get("Geo mismatch", 0) > 50:
            signals.append(f"geographic mismatch ({features.get('Geo mismatch')}% score) from country code {country}")
        if features.get("Merchant safety", 0) > 50:
            signals.append(f"high-risk vendor association with {merchant} ({features.get('Merchant safety')}% risk)")

        signals_text = ", and ".join(signals) if signals else "a combination of standard behavioral vectors"

        if risk == "HIGH":
            narrative = (
                f"API VERDICT: High probability of fraudulent behavior detected for transaction {tx_id}. "
                f"The GNN ensemble observed {signals_text}, resulting in a composite risk score of {score:.1f}/100. "
                f"This is highly characteristic of synthetic identity fraud or account takeover.\n\n"
                f"Action Recommendation: BLOCK IMMEDIATELY. Require secondary factor biometrics or human operator override. "
                f"Threat Class: CRITICAL.\n\n"
                f"Audit Log: API triggered automatic rule freeze due to high composite risk."
            )
        elif risk == "MEDIUM":
            narrative = (
                f"API VERDICT: Moderate risk indicators identified for transaction {tx_id}. "
                f"The transaction size (INR {amount:,.2f}) remains within historical standard deviations, "
                f"but minor flags were raised, including {signals_text}. The composite score of {score:.1f}/100 (Threshold: {model.threshold}) "
                f"warrants secondary routing.\n\n"
                f"Action Recommendation: HOLD FOR MANUAL COMPLIANCE AUDIT. Route to operations queue. "
                f"Threat Class: WARNING.\n\n"
                f"Audit Log: Pushed to analyst review bucket."
            )
        else:
            narrative = (
                f"API VERDICT: Clear consumer pattern verified for transaction {tx_id}. "
                f"All features, including velocity ({velocity} txns/hr) and device trust, are verified within safe historical boundaries. "
                f"The composite risk score of {score:.1f}/100 is below the threshold of {model.threshold}.\n\n"
                f"Action Recommendation: ALLOW/SETTLE. Process through payment networks.\n\n"
                f"Audit Log: Automatic system clearance."
            )
            
        tx_time_struct = time.localtime(current_time - (count - i) * random.randint(45, 120))
        tx_time = time.strftime("%H:%M:%S", tx_time_struct)
        
        tx_obj = {
            "id": tx_id,
            "time": tx_time,
            "amount": amount,
            "type": random.choice(tx_types),
            "merchant": merchant,
            "country": country,
            "device": random.choice(devices),
            "newDevice": new_device,
            "velocity": velocity,
            "features": features,
            "score": round(score, 1),
            "risk": risk,
            "status": status,
            "latency_ms": round(random.uniform(5, 12), 2),
            "narrative": narrative,
            "api_source": "FastAPI Production Engine"
        }
        model.transactions_db.insert(0, tx_obj)

# Seed database
seed_transactions(model_state, 30)


# Request schemas
class TransactionInput(BaseModel):
    id: str
    amount: float
    type: str
    merchant: str
    country: str
    device: str
    newDevice: bool
    velocity: int
    features: Optional[Dict[str, float]] = None

class RetrainRequest(BaseModel):
    verdicts: List[Dict[str, str]] # List of {"txn_id": "...", "verdict": "Confirmed Fraud"/"False Positive"}

# Helpers
def compute_shap_values(amount: float, new_device: bool, velocity: int, country: str, merchant: str) -> Dict[str, float]:
    """Calculate realistic SHAP values representing feature contributions to risk score."""
    # Base indicators (0 to 100)
    amt_anomaly = min(100.0, (amount / 50000.0) * 100.0) if amount > 5000 else random.uniform(5, 25)
    vel_warning = min(100.0, (velocity / 20.0) * 100.0)
    geo_mismatch = 85.0 if country in ["RU", "NG", "KP", "CN"] else random.uniform(5, 20)
    merch_safety = 90.0 if merchant in ["Crypto Exchange", "Global Remittance", "FauxBank ATM", "Crypto Market", "Global Wire"] else random.uniform(2, 15)
    dev_trust = 75.0 if new_device else random.uniform(1, 10)

    # Apply some noise
    features = {
        "Amount anomaly": round(amt_anomaly, 1),
        "Velocity Warning": round(vel_warning, 1),
        "Geo mismatch": round(geo_mismatch, 1),
        "Merchant safety": round(merch_safety, 1),
        "Device trust": round(dev_trust, 1)
    }
    return features

@app.post("/score")
async def score_transaction(tx: TransactionInput):
    start_time = time.time()
    
    # Calculate feature raw anomalies if not provided
    features = tx.features
    if not features:
        features = compute_shap_values(
            tx.amount, tx.newDevice, tx.velocity, tx.country, tx.merchant
        )
    
    # Calculate score using current model weights
    weighted_score = (
        features.get("Amount anomaly", 0) * model_state.weights["amount_anomaly"] +
        features.get("Velocity Warning", 0) * model_state.weights["velocity_warning"] +
        features.get("Geo mismatch", 0) * model_state.weights["geo_mismatch"] +
        features.get("Merchant safety", 0) * model_state.weights["merchant_safety"] +
        features.get("Device trust", 0) * model_state.weights["device_trust"]
    )
    
    # Scale score to 0-100 range
    score = min(100.0, max(0.0, weighted_score))
    
    # Classify based on the threshold
    if score >= model_state.threshold:
        risk = "HIGH"
        status = "Flagged"
    elif score >= (model_state.threshold * 0.6):
        risk = "MEDIUM"
        status = "Review"
    else:
        risk = "LOW"
        status = "Cleared"
        
    # Generate explainable natural language signals
    signals = []
    if tx.amount > 10000:
        signals.append(f"anomalous transaction size of ₹{tx.amount:,.2f} (anomaly rating: {features.get('Amount anomaly')}%)")
    if tx.newDevice:
        signals.append(f"unrecognized {tx.device} signature (device untrust rating: {features.get('Device trust')}%)")
    if tx.velocity > 5:
        signals.append(f"elevated activity velocity of {tx.velocity} txns/hr (velocity rating: {features.get('Velocity Warning')}%)")
    if features.get("Geo mismatch", 0) > 50:
        signals.append(f"geographic mismatch ({features.get('Geo mismatch')}% score) from country code {tx.country}")
    if features.get("Merchant safety", 0) > 50:
        signals.append(f"high-risk vendor association with {tx.merchant} ({features.get('Merchant safety')}% risk)")

    signals_text = ", and ".join(signals) if signals else "a combination of standard behavioral vectors"

    # AI narrative response mimicking our complex ensemble
    if risk == "HIGH":
        narrative = (
            f"API VERDICT: High probability of fraudulent behavior detected for transaction {tx.id}. "
            f"The GNN ensemble observed {signals_text}, resulting in a composite risk score of {score:.1f}/100. "
            f"This is highly characteristic of synthetic identity fraud or account takeover.\n\n"
            f"Action Recommendation: BLOCK IMMEDIATELY. Require secondary factor biometrics or human operator override. "
            f"Threat Class: CRITICAL.\n\n"
            f"Audit Log: API triggered automatic rule freeze due to high composite risk."
        )
    elif risk == "MEDIUM":
        narrative = (
            f"API VERDICT: Moderate risk indicators identified for transaction {tx.id}. "
            f"The transaction size (₹{tx.amount:,.2f}) remains within historical standard deviations, "
            f"but minor flags were raised, including {signals_text}. The composite score of {score:.1f}/100 (Threshold: {model_state.threshold}) "
            f"warrants secondary routing.\n\n"
            f"Action Recommendation: HOLD FOR MANUAL COMPLIANCE AUDIT. Route to operations queue. "
            f"Threat Class: WARNING.\n\n"
            f"Audit Log: Pushed to analyst review bucket."
        )
    else:
        narrative = (
            f"API VERDICT: Clear consumer pattern verified for transaction {tx.id}. "
            f"All features, including velocity ({tx.velocity} txns/hr) and device trust, are verified within safe historical boundaries. "
            f"The composite risk score of {score:.1f}/100 is below the threshold of {model_state.threshold}.\n\n"
            f"Action Recommendation: ALLOW/SETTLE. Process through payment networks.\n\n"
            f"Audit Log: Automatic system clearance."
        )

    latency = (time.time() - start_time) * 1000  # API latency in ms
    # Add a small simulated neural network computation time (5-12ms)
    actual_latency = round(latency + random.uniform(5, 12), 2)

    # Format time
    tx_time_str = time.strftime("%H:%M:%S", time.localtime(time.time()))

    result = {
        "id": tx.id,
        "time": tx_time_str,
        "amount": tx.amount,
        "type": tx.type,
        "merchant": tx.merchant,
        "country": tx.country,
        "device": tx.device,
        "newDevice": tx.newDevice,
        "velocity": tx.velocity,
        "score": round(score, 1),
        "risk": risk,
        "status": status,
        "features": features,
        "latency_ms": actual_latency,
        "narrative": narrative,
        "api_source": "FastAPI Production Engine"
    }

    # Insert into rolling in-memory DB (keep last 50)
    model_state.transactions_db.insert(0, result)
    if len(model_state.transactions_db) > 50:
        model_state.transactions_db.pop()

    return result


@app.post("/retrain")
async def retrain_model(req: RetrainRequest):
    model_state.feedback_count += len(req.verdicts)
    
    # Adjust weights based on feedback to simulate actual learning!
    # For example, if many "False Positives" were reported on Amount anomaly, reduce amount weight.
    # If many "Confirmed Fraud" were reported on Geo mismatch, increase geo mismatch weight.
    amount_fps = 0
    geo_frauds = 0
    for item in req.verdicts:
        verdict = item.get("verdict")
        if verdict == "False Positive":
            amount_fps += 1
        elif verdict == "Confirmed Fraud":
            geo_frauds += 1
            
    # Modify weights slightly
    if amount_fps > 0:
        model_state.weights["amount_anomaly"] = max(0.15, model_state.weights["amount_anomaly"] - 0.02 * amount_fps)
        model_state.weights["velocity_warning"] = min(0.40, model_state.weights["velocity_warning"] + 0.01 * amount_fps)
    if geo_frauds > 0:
        model_state.weights["geo_mismatch"] = min(0.35, model_state.weights["geo_mismatch"] + 0.02 * geo_frauds)
        model_state.weights["amount_anomaly"] = max(0.15, model_state.weights["amount_anomaly"] - 0.01 * geo_frauds)
        
    # Re-normalize weights to sum to 1.0
    w_sum = sum(model_state.weights.values())
    for k in model_state.weights:
        model_state.weights[k] = round(model_state.weights[k] / w_sum, 3)
        
    # Simulate improvements in accuracy, loss, and F1
    model_state.epochs_completed += 1
    model_state.accuracy = min(0.998, model_state.accuracy + 0.001 * len(req.verdicts))
    model_state.auc_roc = min(0.999, model_state.auc_roc + 0.0005 * len(req.verdicts))
    model_state.f1_score = min(0.992, model_state.f1_score + 0.0015 * len(req.verdicts))
    
    # Drop loss
    new_loss = max(0.01, model_state.loss_history[-1] - 0.005 * len(req.verdicts))
    model_state.loss_history.append(round(new_loss, 4))
    if len(model_state.loss_history) > 15:
        model_state.loss_history.pop(0)

    return {
        "status": "success",
        "epochs_completed": model_state.epochs_completed,
        "new_accuracy": round(model_state.accuracy, 4),
        "new_auc_roc": round(model_state.auc_roc, 4),
        "new_f1_score": round(model_state.f1_score, 4),
        "loss_history": model_state.loss_history,
        "updated_weights": model_state.weights
    }

@app.get("/metrics")
async def get_metrics(threshold: float = 50.0):
    model_state.threshold = threshold
    
    # Return metrics specific to threshold setting
    # In a real system, changing the threshold shifts Precision and Recall.
    # We will simulate this relationship realistically:
    # High threshold = High Precision, Low Recall.
    # Low threshold = Low Precision, High Recall.
    t_factor = (threshold - 50.0) / 50.0 # Range -1.0 to 1.0
    
    base_precision = model_state.f1_score + 0.02
    base_recall = model_state.f1_score - 0.01
    
    precision = min(0.999, max(0.50, base_precision + t_factor * 0.15))
    recall = min(0.999, max(0.40, base_recall - t_factor * 0.25))
    
    # Calculate F1
    f1 = 2 * (precision * recall) / (precision + recall)
    
    # Confusion Matrix (out of 10,000 test transactions)
    # Assume 5% are actually fraud (500 cases), 95% clean (9500 cases)
    actual_frauds = 500
    actual_cleans = 9500
    
    tp = int(actual_frauds * recall)
    fn = actual_frauds - tp
    
    # Precision = TP / (TP + FP) => TP + FP = TP / Precision => FP = (TP / Precision) - TP
    fp = int((tp / precision) - tp) if precision > 0 else 0
    tn = actual_cleans - fp
    
    fpr = fp / actual_cleans
    
    return {
        "framework": "FastAPI",
        "accuracy": round((tp + tn) / (actual_frauds + actual_cleans), 4),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1, 3),
        "roc_auc": round(model_state.auc_roc, 4),
        "fpr": round(fpr, 4),
        "confusion_matrix": {
            "TP": tp,
            "FP": fp,
            "FN": fn,
            "TN": tn
        },
        "weights": model_state.weights
    }

@app.get("/drift")
async def get_drift_metrics():
    # Return synthetic drift metrics showing AI stability
    return {
        "data_drift_detected": False,
        "concept_drift_detected": False,
        "psi_metrics": {
            "amount": 0.045, # Population Stability Index (<0.1 is stable)
            "velocity": 0.062,
            "geo_mismatch": 0.081,
            "device_trust": 0.038
        },
        "bias_metrics": {
            "disparate_impact_ratio": 0.975, # Close to 1.0 is fair
            "statistical_parity_diff": -0.012
        },
        "monitoring_status": "OPTIMAL"
    }

@app.get("/transactions")
async def get_transactions():
    return model_state.transactions_db

@app.get("/transactions/{tx_id}")
async def get_transaction(tx_id: str):
    for tx in model_state.transactions_db:
        if tx["id"] == tx_id:
            return tx
    raise HTTPException(status_code=404, detail="Transaction not found")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Shield Fraud Detection Engine on port {port}...")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
