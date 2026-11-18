# KubeDoctor — Kubernetes Monitoring and Automated Diagnosis

KubeDoctor is a Kubernetes monitoring and diagnosis project that identifies common pod problems, monitors container memory usage, detects unusual memory patterns using Machine Learning, and sends alerts through Telegram.

## Features

- **Kubernetes monitoring:** Reads pod and container status using the Kubernetes Python client.
- **Prometheus integration:** Collects container memory usage and monitoring metrics.
- **Grafana dashboard:** Visualizes total pods, healthy pods, unhealthy pods, memory usage, and container restarts.
- **Automated diagnosis:** Identifies image-pull failures, repeated container crashes, and memory-limit issues.
- **Machine Learning:** Uses Isolation Forest to detect unusual memory usage.
- **Telegram notifications:** Sends alerts when a pod needs attention.

## Technologies Used

- Python
- Kubernetes
- Minikube
- Docker
- Prometheus
- Grafana
- Helm
- Scikit-learn
- Isolation Forest
- Telegram Bot API

## Project Structure

```text
KubeDoctor/
│
├── bot/
│   ├── kubedoctor.py
│   ├── kubernetes_check.py
│   ├── prometheus_check.py
│   └── telegram_test.py
│
├── dashboards/
│   └── kubedoctor-dashboard.json
│
├── k8s/
│   ├── bad-image.yaml
│   ├── crasher.yaml
│   ├── leaky-app.yaml
│   ├── memory-hog.yaml
│   └── monitoring-values.yaml
│
├── ml/
│   ├── check_metrics.py
│   ├── detect_anomaly.py
│   ├── memory_model.pkl
│   ├── train_anomaly.py
│   └── training_data.csv
│
├── .gitignore
├── requirements.txt
└── README.md
```

## Demo Scenarios

KubeDoctor uses four demo workloads to test different conditions:

| Workload | Purpose |
|---|---|
| memory-hog | Demonstrates memory consumption |
| bad-image | Simulates an image-pull failure |
| crasher | Simulates repeated container crashes |
| leaky-app | Simulates memory growth and OOMKilled restarts |

## Setup and Installation

### 1. Prerequisites

Install the following tools:

- Docker Desktop
- Minikube
- kubectl
- Helm
- Python 3.12

Start Minikube:

```powershell
minikube start --cpus=4 --memory=5120 --driver=docker
```

### 2. Clone the repository

```powershell
git clone https://github.com/707Piyush/KubeDoctor.git
cd KubeDoctor
```

### 3. Create and activate a Python environment

```powershell
python -m venv .venv
```

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

### 4. Install the monitoring stack

Create the monitoring namespace:

```powershell
kubectl create namespace monitoring
```

Add the Prometheus Helm repository:

```powershell
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

Before installing, set a secure Grafana admin password in `k8s/monitoring-values.yaml`. Do not commit real passwords or tokens.

Install Prometheus, Grafana, and Alertmanager:

```powershell
helm upgrade --install kube-doctor prometheus-community/kube-prometheus-stack --namespace monitoring --values .\k8s\monitoring-values.yaml --wait --timeout 10m
```

Enable Metrics Server:

```powershell
minikube addons enable metrics-server
```

### 5. Deploy demo workloads

Create the demo namespace:

```powershell
kubectl create namespace demo
```

Apply the demo configurations:

```powershell
kubectl apply -f .\k8s\memory-hog.yaml
kubectl apply -f .\k8s\bad-image.yaml
kubectl apply -f .\k8s\crasher.yaml
kubectl apply -f .\k8s\leaky-app.yaml
```

Check the pods:

```powershell
kubectl get pods -n demo
```

### 6. Configure Telegram alerts

Create a Telegram bot using BotFather and obtain its bot token.

Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

Keep `.env` private. It is excluded from Git using `.gitignore`.

### 7. Start Prometheus access

Open a separate terminal and run:

```powershell
kubectl port-forward -n monitoring svc/kube-doctor-kube-prometheu-prometheus 9090:9090
```

Keep this terminal running while using the Python monitoring scripts.

### 8. Train the ML model

From the project root:

```powershell
python .\ml\train_anomaly.py
```

### 9. Run KubeDoctor

```powershell
python .\bot\kubedoctor.py
```

The program checks demo pods, reads available Prometheus memory metrics, runs the anomaly model, prints a diagnosis, and sends Telegram alerts for pods that need attention.

## Grafana Dashboard

The exported dashboard configuration is available at:

`dashboards/kubedoctor-dashboard.json`

The dashboard includes panels for:

- Total Kubernetes pods
- Healthy pods
- Unhealthy pods
- Pod memory usage
- Container restart count

## Machine Learning Note

The current Isolation Forest model is trained using synthetic sample memory-usage data. Its anomaly predictions are experimental and intended for this project demonstration, not production-grade prediction.

## Project Status

This is an academic and portfolio-oriented MVP tested on a local Minikube cluster. It demonstrates Kubernetes monitoring, automated diagnosis, metrics visualization, experimental anomaly detection, and Telegram notifications.

## Author

**Piyush Gupta**

GitHub: https://github.com/707Piyush