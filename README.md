# 💳 Fraud Detection ML Inference Platform

A production-oriented fraud detection platform built with **XGBoost, FastAPI, Redis, Docker, and Gunicorn**.

The system combines **Bayesian-tuned machine learning models**, **business-driven threshold optimization**, and **production-ready deployment practices** to support both real-time and batch fraud detection workloads.

---

# Live Demo

**API Base URL**

https://fraud-model-image-latest.onrender.com

**Interactive API Documentation**

https://fraud-model-image-latest.onrender.com//docs

---
## Business Goal

Credit card fraud detection is a highly imbalanced classification problem where fraudulent transactions represent only a small fraction of total activity.

The objective is to:

* Detect fraudulent transactions as early as possible
* Minimize financial losses
* Reduce false positives that impact legitimate customers
* Support scalable fraud monitoring workflows

---

## Features

* Real-time fraud prediction (`/predict`)
* Batch CSV fraud scoring (`/predict/csv`)
* Redis-backed metrics (`/metrics`)
* Health monitoring (`/health`)
* Model metadata & versioning
* Rate limiting
* Structured logging
* Request tracing using UUIDs
* Dockerized deployment
* Multi-worker serving with Gunicorn

---

## Machine Learning Approach

### Model Development

* XGBoost Classifier
* Bayesian Hyperparameter Optimization
* Class imbalance handling using `scale_pos_weight`
* Business-aligned threshold tuning using Precision-Recall analysis

### Threshold Optimization

Instead of using the default classification threshold (`0.5`), the deployed threshold was selected using **Precision-Recall Curve analysis**.

The primary objective was to maximize precision while maintaining an acceptable level of recall. During evaluation, candidate thresholds were analyzed on the Precision-Recall curve, and a threshold was selected from the region where:

- Precision ≥ 95%
- Recall ≥ 83%

These values were used as threshold selection criteria rather than optimization targets themselves. The resulting threshold was then deployed as part of the inference service to support high-confidence fraud detection while limiting false positive predictions.ves that could impact legitimate customers.

---

## Architecture

```text
Client
  │
  ▼
FastAPI
  │
  ▼
Gunicorn Workers
  │
  ├── Real-Time Inference
  ├── Batch CSV Processing
  └── Metrics Collection
  │
  ▼
Redis
  │
  ▼
XGBoost Fraud Detection Model
```

---

## API Endpoints

| Endpoint              | Description                     |
| --------------------- | ------------------------------- |
| `POST /predict`       | Real-time fraud prediction      |
| `POST /predict/csv`   | Batch fraud detection using CSV |
| `GET /metrics`        | Runtime metrics and statistics  |
| `GET /health`         | Service health check            |
| `GET /health/details` | Detailed service status         |
| `GET /model/info`     | Model metadata                  |

---

## Tech Stack

### Machine Learning

* XGBoost
* Scikit-learn
* Pandas
* NumPy

### Backend

* FastAPI
* Pydantic
* Gunicorn

### Infrastructure

* Docker
* Docker Compose
* Redis

### Monitoring & Observability

* Structured Logging
* Runtime Metrics
* Health Checks

---

## Project Structure

```text
app/
├── auth.py
├── config.py
├── logger.py
├── main.py
├── redis_client.py
├── routes.py
├── schemas.py
├── services.py
└── logs/
    └── app.logs
    
models/
└── model.pkl

Dockerfile
docker-compose.yml
requirements.txt
.env
```

---

## Running Locally

Clone the repository:

```bash
git clone https://github.com/nabeelsyedwork-tech/fraud-detection-ml-platform.git
cd fraud-detection-platform
```

Environment variables:
```text
Use the existing env in the repository
```


Start the application:

```bash
docker compose up --build
```

API Documentation:

```text
http://localhost:8000/docs
```

---

## Example Requests

Sample request files are available in the `examples/` directory:

- `sample_transaction.json` → Real-time prediction example
- `sample_batch.csv` → Batch prediction example

---
## Authentication

Protected endpoints require HTTP Basic Authentication.

Demo credentials:

```text
Username: admin
Password: admin123
```

Protected Endpoints:

- `POST /predict`
- `POST /predict/csv`
- `GET /metrics`
- `GET /model/info`

These credentials are configured through environment variables and are intended for demonstration and local development purposes.

---

## Key Engineering Decisions

* Startup validation for model loading
* Redis-backed metrics for multi-worker consistency
* Gunicorn workers for concurrent inference
* Structured logging and request tracing
* Rate limiting for API protection
* Bayesian hyperparameter tuning
* Precision-Recall curve based threshold selection
* Business-aligned deployment threshold instead of default model thresholds

---

## Future Improvements

* Prometheus & Grafana Monitoring
* CI/CD with GitHub Actions
* MLflow Model Registry
* JWT Authentication
* Kubernetes Deployment

---

## Dataset

The original dataset is not included due to file size limitations.

Dataset:
**Credit Card Fraud Detection Dataset (Kaggle)**

---

## Status

✅ Production-Oriented MVP Complete

This project demonstrates the transition from machine learning experimentation to a deployable fraud detection platform with scalable inference, monitoring, observability, and containerized infrastructure.

### Deployment

- Dockerized
- Redis-backed metrics
- Multi-worker serving with Gunicorn
- Deployed on Render
