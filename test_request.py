import requests
import json

url = "http://127.0.0.1:8000/predict"

payload = [
    {"driverId": "max_verstappen", "constructorId": "red_bull", "grid": 1, "Location": "Monza"},
    {"driverId": "leclerc", "constructorId": "ferrari", "grid": 2, "Location": "Monza"},
    {"driverId": "hamilton", "constructorId": "ferrari", "grid": 3, "Location": "Monza"},
    {"driverId": "norris", "constructorId": "mclaren", "grid": 4, "Location": "Monza"}
]

try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("API Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except requests.exceptions.ConnectionError:
    print("Could not connect to the API. Is it running?")
