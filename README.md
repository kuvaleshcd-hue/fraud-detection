# Shield Fraud Operations Console

An advanced, real-time AI-powered Fraud Detection System (FDS) and Explainable Neural Risk Intelligence Engine. This project is built specifically to address **Track 1, Problem Statement 2** of the Hackathon.

## Quick Start for the Jury

You can run and test this project in **two ways** depending on your environment. Both modes are fully functional and interactive:

### Option A: Zero-Install / Sandbox Mode (Recommended for Instant Review)
1. **Navigate to the project folder.**
2. **Double-click `index.html`** to open it directly in any modern web browser.
3. The dashboard will automatically activate its **Simulated Hybrid ML Engine** and function 100% locally out-of-the-box (no installation, no servers, no dependencies).

### Option B: Full-Stack Docker Container Mode (For API Verification)
1. Ensure you have **Docker** and **Docker Compose** installed.
2. Run the following command in the project root:
   ```bash
   docker-compose up --build
   ```
3. Open your browser and navigate to:
   - **Analyst Dashboard (Frontend)**: [http://localhost](http://localhost)
   - **Inference API (Backend)**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
4. The dashboard will automatically detect the backend on load and switch its status banner to **LIVE REST API (FastAPI)**.

---

## 9 Expected Outcomes & How to Test Them

Here is the checklist of the 9 required outcomes. You can interact with each of them live:

### 1. Low-Latency Real-Time Inference (< 200 ms)
- **What it is**: The system scores incoming transactions instantly.
- **How to test**: Look at the **Model Latency** card in the top stats strip. The latency is measured live per transaction (averaging between **5ms and 15ms**, which is well below the 200ms threshold).

### 2. Interactive Analyst Dashboard
- **What it is**: A high-tech operations interface monitoring live financial traffic.
- **How to test**: In the **Operations Feed** tab, you will see a live-scrolling queue of transactions. The stats cards and Recharts charts (anomaly density & risk ratio) update in real-time as transactions flow in. You can pause the stream using the **Pause Feed** button at the top right.

### 3. GNN (Graph Neural Network) Account Subgraph
- **What it is**: A visualization of account relationships (User, Cards, Device, Location, Merchant) to detect multi-hop fraud networks.
- **How to test**: Click on any transaction row in the logs table. It will take you to the **Threat Intelligence & GNN** tab. In the center, you will see a live physics-based canvas graph where nodes float and links pulse. **Hover your cursor** over nodes (e.g. Device, Merchant) to see their individual risk contributions.

### 4. Explainable AI (SHAP Feature Attribution)
- **What it is**: Visual proof explaining *why* the AI flagged a transaction.
- **How to test**: In the **Threat Intelligence & GNN** tab (after selecting a transaction), view the **Feature Attribution Weights (SHAP)** bar charts. They display contribution percentages for vectors like *Amount Anomaly*, *Velocity Warning*, and *Geo Mismatch*. An AI-written **Neural Explanatory Log** displays a narrative of the risk factors.

### 5. Adaptive Decision Boundary Tuning
- **What it is**: Threshold optimization tool to control false positives and recall.
- **How to test**: Navigate to the **Decision Boundary Tuning** tab. Drag the **Classification Cutoff Score** slider. As you slide, the **Confusion Matrix** cards (TP, FP, FN, TN) and accuracy metrics recalculate *instantly*. A cursor dot moves along the **ROC-AUC** and **Precision-Recall** curves to reflect the current threshold.

### 6. Continuous Feedback Retraining Pipeline
- **What it is**: Machine learning model adapting to human-in-the-loop analyst decisions.
- **How to test**:
  1. Go to the **Threat Intelligence** tab, select a transaction, and click **Confirm Fraud** or **False Alarm** to log analyst overrides.
  2. Navigate to the **Feedback Retraining** tab.
  3. Click the **Retrain Engine** button. A console will log training epochs in real time, and the **Loss History** chart will animate as loss drops, updating the model parameters.

### 7. Model Monitoring & Data Drift
- **What it is**: Monitoring checks to detect changes in customer spending habits (data drift) or attack profiles (concept drift).
- **How to test**: Go to the **Governance & Data Drift** tab to see live Population Stability Index (PSI) values for each feature, tracking stable and drifting metrics.

### 8. Compliance & Fairness Metrics
- **What it is**: Bias monitoring indicators to ensure fairness.
- **How to test**: In the **Governance & Data Drift** tab, inspect the **Disparate Impact Ratio** and **Statistical Parity Difference** gauges to confirm compliance under fair lending laws.

### 9. System Architecture & Code Deployment Templates
- **What it is**: Cloud-native design schematics.
- **How to test**: Navigate to the **Architecture & Code Deploy** tab. Review the interactive pipeline chart and use the copy buttons to fetch the production deployment files.

---

## Under the Hood: AI Architecture

1. **Feature Engineering**: Standardizes amounts, calculates rolling transaction velocity (transactions per hour), matches device fingerprints against user history, and correlates geolocation coordinates.
2. **SMOTE Oversampling**: Backend pipelines utilize SMOTE to handle the severe class imbalance (where fraud represents < 1% of transactions).
3. **Hybrid Ensemble**:
   - **GNN (Graph Neural Network)**: Evaluates account connection subgraphs to identify mule account patterns.
   - **Transformer**: Models sequential transaction behavior over time to detect anomalies.
4. **FastAPI Server**: Employs Uvicorn and Pydantic validation to serve real-time predictions under 15ms.
