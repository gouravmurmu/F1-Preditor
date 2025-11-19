# Deployment Instructions

## Local Deployment
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the API:
   ```bash
   uvicorn app:app --reload
   ```
3. Access the API documentation at `http://localhost:8000/docs`.

## Docker Deployment
1. Build the image:
   ```bash
   docker build -t f1-prediction-api .
   ```
2. Run the container:
   ```bash
   docker run -p 8000:8000 f1-prediction-api
   ```

## Cloud Deployment (e.g., Render/Railway)
1. Push this repository to GitHub.
2. Connect your GitHub repo to Render/Railway.
3. Set the build command to `pip install -r requirements.txt`.
4. Set the start command to `uvicorn app:app --host 0.0.0.0 --port $PORT`.
