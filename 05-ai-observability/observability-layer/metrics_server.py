from prometheus_client import start_http_server
import time

if __name__ == "__main__":
    start_http_server(8000)
    print("🚀 Prometheus metrics server started at http://localhost:8000/metrics")
    while True:
        time.sleep(60)