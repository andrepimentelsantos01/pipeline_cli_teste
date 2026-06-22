import requests


INTERNAL_API_URL = "http://127.0.0.1:8000/clients"

def send_client(client, timeout=5):
    try:
        response = requests.post(
            INTERNAL_API_URL,
            json=client,
            timeout=timeout,
        )

        if response.status_code == 201:
            return "created"

        if response.status_code == 200:
            return "updated"

        return "failed"

    except requests.RequestException:
        return "failed"