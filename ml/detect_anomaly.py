
import requests
import joblib
import pandas as pd


PROMETHEUS_URL = "http://localhost:9090"

model = joblib.load("ml/memory_model.pkl")


def get_memory_metrics():

    query = (
        'container_memory_working_set_bytes'
        '{namespace="demo", container!="", container!="POD"}'
        ' / 1024 / 1024'
    )

    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query",
        params={"query": query},
        timeout=10
    )

    response.raise_for_status()

    return response.json()["data"]["result"]


def detect_anomalies():

    print("\n====================================")
    print("   KUBEDOCTOR ML ANOMALY REPORT")
    print("====================================")

    results = get_memory_metrics()

    memory_data = {}

    for item in results:

        pod_name = item["metric"].get("pod")

        memory = float(item["value"][1])

        if pod_name:
            memory_data[pod_name] = memory

    # Get all pods from Kubernetes
    from kubernetes import client, config

    config.load_kube_config()

    v1 = client.CoreV1Api()

    pods = v1.list_namespaced_pod(namespace="demo")

    for pod in pods.items:

        pod_name = pod.metadata.name

        print("\nPod:", pod_name)

        if pod_name not in memory_data:
            print("ML Result: Memory metrics unavailable")
            continue

        memory = memory_data[pod_name]

        prediction = model.predict(
            pd.DataFrame({"memory_usage": [memory]})
        )[0]

        print(f"Memory usage: {memory:.2f} MiB")

        if prediction == -1:
            print("ML Result: ANOMALY DETECTED")
        else:
            print("ML Result: Normal memory usage")


if __name__ == "__main__":

    try:
        detect_anomalies()

    except requests.RequestException as error:
        print("Prometheus connection error:", error)

    except Exception as error:
        print("KubeDoctor error:", error)

