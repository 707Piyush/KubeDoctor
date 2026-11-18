
import requests

url = "http://localhost:9090/api/v1/query"

query = 'container_memory_working_set_bytes{namespace="demo",container!="",container!="POD"}'

response = requests.get(
    url,
    params={"query": query},
    timeout=10
)

response.raise_for_status()

results = response.json()["data"]["result"]

print("\n===== CURRENT MEMORY METRICS =====")

if not results:
    print("No memory metrics available.")

for item in results:
    pod = item["metric"].get("pod", "Unknown")
    memory = float(item["value"][1]) / (1024 * 1024)

    print(f"Pod: {pod}")
    print(f"Memory: {memory:.2f} MiB")
    print("-------------------------")
