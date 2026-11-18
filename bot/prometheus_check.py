
import requests

PROMETHEUS_URL = "http://localhost:9090"

def get_metrics(query):
    url = f"{PROMETHEUS_URL}/api/v1/query"

    response = requests.get(
        url,
        params={"query": query},
        timeout=10
    )

    response.raise_for_status()
    return response.json()["data"]["result"]


# Get container restart counts
restart_query = 'kube_pod_container_status_restarts_total{namespace="demo"}'

# Get container memory usage in MiB
memory_query = 'container_memory_working_set_bytes{namespace="demo", container!="", container!="POD"} / 1024 / 1024'

print("\n===== KUBEDOCTOR: POD RESTARTS =====")

for item in get_metrics(restart_query):
    pod = item["metric"]["pod"]
    restarts = item["value"][1]

    print(f"Pod: {pod} | Restarts: {restarts}")


print("\n===== KUBEDOCTOR: MEMORY USAGE =====")

for item in get_metrics(memory_query):
    pod = item["metric"]["pod"]
    memory = float(item["value"][1])

    print(f"Pod: {pod} | Memory: {memory:.2f} MiB")
