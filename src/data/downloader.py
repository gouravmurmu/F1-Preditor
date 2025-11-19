import os
import requests
import zipfile
import io

def download_ergast_data(output_dir):
    """Downloads and extracts Ergast F1 data (CSV tables)."""
    url = "https://github.com/vopani/ergast-f1-api-csv/archive/refs/heads/main.zip"
    print(f"Downloading data from {url}...")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    print("Extracting data...")
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(output_dir)
    
    print(f"Data downloaded and extracted to {output_dir}")

if __name__ == "__main__":
    raw_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "raw")
    os.makedirs(raw_data_dir, exist_ok=True)
    download_ergast_data(raw_data_dir)
