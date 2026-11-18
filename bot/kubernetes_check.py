
from kubernetes import client, config
from kubernetes.client.rest import ApiException


def check_kubernetes():
    print("\n================================")
    print("       KUBEDOCTOR REPORT")
    print("================================")

    try:
        # Connect to Minikube using your kubeconfig
        config.load_kube_config()

        # Create Kubernetes API connection
        v1 = client.CoreV1Api()

        # Get all pods from demo namespace
        pods = v1.list_namespaced_pod(namespace="demo")

        print("\nChecking demo namespace...\n")

        for pod in pods.items:
            pod_name = pod.metadata.name
            pod_phase = pod.status.phase

            print("--------------------------------")
            print("Pod:", pod_name)
            print("Status:", pod_phase)

            if not pod.status.container_statuses:
                print("Diagnosis: Container status not available")
                continue

            for container in pod.status.container_statuses:

                # Check if container is waiting
                if container.state.waiting:
                    reason = container.state.waiting.reason

                    if reason == "ImagePullBackOff":
                        print("Problem: Image cannot be downloaded")

                    elif reason == "ErrImagePull":
                        print("Problem: Image pull failed")

                    elif reason == "CrashLoopBackOff":
                        print("Problem: Container is repeatedly crashing")

                    else:
                        print("Waiting reason:", reason)

                # Check previous container termination
                if container.last_state.terminated:
                    reason = container.last_state.terminated.reason

                    if reason == "OOMKilled":
                        print("Problem: Container exceeded memory limit (OOMKilled)")

                    elif reason == "Error":
                        print("Problem: Container terminated with an error")

                # Check restart count
                print("Restart count:", container.restart_count)

            if pod_phase == "Running":
                print("Pod is currently running.")

    except ApiException as error:
        print("Kubernetes API error:", error)

    except Exception as error:
        print("Error:", error)


if __name__ == "__main__":
    check_kubernetes()
