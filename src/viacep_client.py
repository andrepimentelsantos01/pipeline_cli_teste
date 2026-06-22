import requests

VIACEP_URL = "https://viacep.com.br/ws/{zip_code}/json/"

def get_address_by_zip_code(zip_code, timeout=5):
    if not zip_code:
        return None


    try:
        response = requests.get(
            VIACEP_URL.format(zip_code=zip_code),
            timeout=timeout
        )

        response.raise_for_status()
        data = response.json()

        if data.get("erro"):
            return None

        return {
            "street": data.get("logradouro", ""),
            "neighborhood": data.get("bairro", ""),
            "city": data.get("localidade", ""),
            "state": data.get("uf", ""),
        }

    except requests.RequestException:
        return None