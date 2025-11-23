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

## Free Cloud Deployment (Recommended: Hugging Face Spaces)

This project is configured for **free** deployment on Hugging Face Spaces using Docker.

### Steps to Deploy
1.  **Create an Account**: Go to [huggingface.co](https://huggingface.co) and create a free account.
2.  **Create a New Space**:
    *   Click on your profile picture -> **New Space**.
    *   **Space Name**: `f1-predictor` (or similar).
    *   **License**: MIT (optional).
    *   **Space SDK**: Select **Docker**.
    *   **Space Hardware**: Select **Free** (CPU Basic - 2 vCPU, 16GB RAM).
    *   Click **Create Space**.
3.  **Upload Code**:
    *   You can clone the repository provided by Hugging Face and copy your files into it.
    *   **OR** (Easier) Go to the **Files** tab of your new Space, click **Add file** -> **Upload files**, and drag & drop all your project files (including `Dockerfile`, `requirements.txt`, `app.py`, `src/`, `data/`, etc.).
    *   Commit the changes.
4.  **Wait for Build**: The Space will automatically build the Docker image. This may take a few minutes.
5.  **Enjoy**: Once built, your app will be live at `https://huggingface.co/spaces/<your-username>/<space-name>`.

### Important Notes
- **Port**: The `Dockerfile` is configured to expose port `7860`, which is required by Hugging Face Spaces.
- **Permissions**: The Docker container runs as a non-root user (ID 1000) for security compliance.

