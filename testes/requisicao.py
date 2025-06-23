import requests

url = 'http://localhost:8000/parametros'

for i in range(10):
    response = requests.get(url)
    print(f"Requisição {i+1}: {response.status_code} - {response.json()}")