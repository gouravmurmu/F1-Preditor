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

## Free Cloud Deployment (Recommended: Render.com)

This project is configured for easy deployment on Render, which offers a free tier for web services.

### Option 1: "Deploy to Render" Button (Easiest)
1. Push this code to a GitHub repository.
2. Create a Render account at [render.com](https://render.com).
3. In Render, click **New +** and select **Blueprint**.
4. Connect your GitHub account and select your repository.
5. Render will automatically detect the `render.yaml` file and configure the service.
6. Click **Apply** to deploy. 

### Option 2: Manual Setup
1. Push this code to a GitHub repository.
2. Create a Render account at [render.com](https://render.com).
3. Click **New +** and select **Web Service**.
4. Connect your GitHub repository.
5. Configure the following settings:
   - **Name**: `f1-predictor` (or any name you like)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
6. Scroll down and select the **Free** instance type.
7. Click **Create Web Service**.

### Important Notes for Free Tier
- **Spin Down**: On the free tier, the service will "sleep" after 15 minutes of inactivity. The first request after sleeping may take 30-60 seconds to load.
- **Resources**: You have limited RAM (512MB). This should be enough for this model, but if you see "Out of Memory" errors, you may need to optimize the model size or upgrade.

