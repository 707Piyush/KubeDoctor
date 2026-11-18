
import requests
import joblib
import pandas as pd
import os

from dotenv import load_dotenv
from kubernetes import client, config


# ==========================================
# CONFIGURATION
# ==========================================

PROMETHEUS_URL = "http://localhost:9090"
MODEL_PATH = "ml/memory_model.pkl"

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# ==========================================
# TELEGRAM ALERT FUNCTION
# ==========================================

def send_telegram_alert(message):

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram settings are missing.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        response = requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message
            },
            timeout=10
        )

        response.raise_for_status()

        print("Telegram alert sent!")

    except requests.RequestException as error:
        print("Telegram alert failed:", error)


# ==========================================
# GET MEMORY METRICS FROM PROMETHEUS
# ==========================================

def get_memory_metrics():

    query = (
        'container_memory_working_set_bytes'
        '{namespace="demo", container!="", container!="POD"}'
        ' / 1024 / 1024'
    )

    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": query},
            timeout=10
        )

        response.raise_for_status()

        results = response.json()["data"]["result"]

        memory_data = {}

        for item in results:

            pod_name = item["metric"].get("pod")
            memory = float(item["value"][1])

            if pod_name:
                memory_data[pod_name] = memory

        return memory_data

    except requests.RequestException as error:

        print("Prometheus connection problem:", error)

        return None


# ==========================================
# MAIN KUBERNETES DIAGNOSIS
# ==========================================

def check_pods():

    # Load trained ML model
    model = joblib.load(MODEL_PATH)

    # Connect to Kubernetes
    config.load_kube_config()

    v1 = client.CoreV1Api()

    pods = v1.list_namespaced_pod(namespace="demo")

    # Get memory readings
    memory_data = get_memory_metrics()

    print("\n========================================")
    print("          KUBEDOCTOR REPORT")
    print("========================================")

    for pod in pods.items:

        pod_name = pod.metadata.name
        pod_phase = pod.status.phase

        print("\n----------------------------------------")
        print("Pod:", pod_name)
        print("Status:", pod_phase)

        if not pod.status.container_statuses:

            print("Diagnosis: Container status unavailable")
            print("ML Result: Not available")
            continue

        all_ready = True
        has_problem = False

        problems = []

        # Check container status
        for container in pod.status.container_statuses:

            print("Container:", container.name)
            print("Restart count:", container.restart_count)

            if not container.ready:

                all_ready = False

            # Check current waiting state
            if container.state.waiting:

                has_problem = True

                reason = container.state.waiting.reason

                if reason in ["ImagePullBackOff", "ErrImagePull"]:

                    problem = "Image pull failed"

                elif reason == "CrashLoopBackOff":

                    problem = "Container is repeatedly crashing"

                else:

                    problem = f"Container waiting: {reason}"

                print("Problem:", problem)

                if problem not in problems:
                    problems.append(problem)

            # Check previous container termination
            if container.last_state.terminated:

                reason = container.last_state.terminated.reason

                if reason == "OOMKilled":

                    problem = "Container exceeded its memory limit"

                    has_problem = True

                    print("Problem:", problem)

                    if problem not in problems:
                        problems.append(problem)

                elif reason == "Error":

                    problem = "Container terminated with an error"

                    has_problem = True

                    print("Problem:", problem)

                    if problem not in problems:
                        problems.append(problem)

        # ==================================
        # MEMORY AND ML PREDICTION
        # ==================================

        if memory_data is not None and pod_name in memory_data:

            memory = memory_data[pod_name]

            print(f"Memory usage: {memory:.2f} MiB")

            prediction = model.predict(
                pd.DataFrame({
                    "memory_usage": [memory]
                })
            )[0]

            if prediction == -1:

                print("ML Result: ANOMALY DETECTED")

                has_problem = True

                problems.append("Unusual memory usage detected by ML")

            else:

                print("ML Result: Normal memory usage")

        else:

            print("Memory usage: Not currently available")
            print("ML Result: Memory metrics unavailable")

        # ==================================
        # FINAL DIAGNOSIS AND TELEGRAM ALERT
        # ==================================

        if pod_phase == "Running" and all_ready and not has_problem:

            print("Diagnosis: Pod is healthy")

        else:

            print("Diagnosis: Pod needs attention")

            problem_details = "\n".join(problems)

            if not problem_details:
                problem_details = "Pod is not ready or is not running"

            alert_message = (
                "🚨 KUBEDOCTOR ALERT 🚨\n\n"
                f"Pod: {pod_name}\n"
                "Namespace: demo\n"
                f"Status: {pod_phase}\n\n"
                f"Problems:\n{problem_details}\n\n"
                "Please check your Kubernetes cluster."
            )

            # Send alert ONLY for unhealthy pods
            send_telegram_alert(alert_message)


# ==========================================
# PROGRAM START
# ==========================================

if __name__ == "__main__":

    try:

        check_pods()

    except Exception as error:

        print("KubeDoctor error:", error)
