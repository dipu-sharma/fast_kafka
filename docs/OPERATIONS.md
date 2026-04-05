# 🚀 FastAPI Modular Banking - CI/CD & Operations Guide

This document provides complete instructions for running the FastAPI application and its associated DevOps stack (Jenkins, SonarQube, Prometheus, Grafana).

---

## 🏗️ Architecture Overview

- **App Stack**: 4 FastAPI Microservices (Accounts, Payments, Profiles, Transactions), Kafka, Zookeeper, and PostgreSQL.
- **DevOps Stack**: Jenkins (CI/CD), SonarQube (Quality), Trivy (Security), Prometheus (Metrics), Grafana (Visualization).
- **CD Strategy**: GitOps with ArgoCD and Kubernetes (Production-ready).

---

## 🛠️ Prerequisites

- **Docker & Docker Compose** installed.
- **Python 3.9+** (for local development).
- **Git** (for version control).

---

## 🏃 1. Quick Start (Docker Compose)

To run the entire ecosystem locally:

### Step A: Start the Application Stack
```bash
docker-compose up -d
```
This starts the databases, Kafka brokers, and the 4 FastAPI services.

### Step B: Start the DevOps Stack
```bash
docker-compose -f devops-stack.yml up -d
```
This starts Jenkins, SonarQube, Prometheus, and Grafana.

---

## 🔗 2. Dashboard Access

| Tool | Local URL | Default Credentials |
| :--- | :--- | :--- |
| **FastAPI (Accounts)** | `http://localhost:8001/docs` | - |
| **Jenkins** | `http://localhost:8080` | Check logs: `docker logs jenkins` |
| **SonarQube** | `http://localhost:9000` | `admin` / `admin` |
| **Prometheus** | `http://localhost:9090` | - |
| **Grafana** | `http://localhost:3000` | `admin` / `admin` |

---

## 🔄 3. CI/CD Pipeline Flow

The `Jenkinsfile` at the root automates the following flow:

1.  **Pytest & Coverage**: Runs tests and generates `coverage.xml`.
2.  **OWASP Scan**: Scans for vulnerable Python dependencies.
3.  **SonarQube Analysis**: Reports code quality and bugs.
4.  **Docker Build**: Builds the production-ready image.
5.  **Trivy Security Scan**: Fails the build if `CRITICAL` vulnerabilities are found.
6.  **Docker Push**: Pushes to your registry.
7.  **ArgoCD Update**: Updates `k8s/deployment.yaml` with the new image tag.

---

## 📊 4. Monitoring (Prometheus & Grafana)

1.  Open **Grafana** (`localhost:3000`).
2.  Add **Data Source**: Select `Prometheus`.
3.  URL: `http://prometheus:9090`.
4.  Import a **FastAPI Dashboard** or create a new one to track:
    -   `fastapi_requests_total`
    -   `fastapi_request_duration_seconds_bucket`

---

## 🧪 5. Local Development & Testing

### Install Dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Tests Manually
```bash
pytest --cov=. --cov-report=term-missing
```

### Run Services Individually
```bash
uvicorn services.accounts.main:app --port 8000
```

---

## 📦 6. Kubernetes Deployment (Production)

To deploy to Kubernetes using the provided manifests:

1.  **Apply Manifests**:
    ```bash
    kubectl apply -f k8s/
    ```
2.  **ArgoCD Setup**:
    Point ArgoCD to the `k8s/` folder in your Git repository.
