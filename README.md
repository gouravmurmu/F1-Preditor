# F1 2026 Prediction System

![F1 Predictor](https://img.shields.io/badge/F1-Predictor-red) ![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Docker](https://img.shields.io/badge/Docker-Ready-blue)

A machine learning-powered application to predict Formula 1 race winners. This project uses historical data and XGBoost to generate win probabilities for drivers based on their grid position, recent form, and track characteristics.

## 🚀 Features

*   **Race Winner Prediction**: Predicts the probability of each driver winning.
*   **Interactive Web Interface**: User-friendly HTML frontend to set up the grid and view results.
*   **REST API**: FastAPI backend for programmatic access.
*   **Dockerized**: Ready for deployment with Docker.
*   **Historical Data**: Trained on 2023-2024 race data (extensible).

## 🛠️ Installation

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/gouravmurmu/F1-Preditor.git
    cd F1-Preditor
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python app.py
    ```

4.  **Access the app:**
    Open your browser to `http://127.0.0.1:5000`.

### Docker Setup

1.  **Build the image:**
    ```bash
    docker build -t f1-predictor .
    ```

2.  **Run the container:**
    ```bash
    docker run -p 5000:5000 f1-predictor
    ```

## 📖 Usage

1.  Select the **Circuit / Location** from the dropdown.
2.  Add drivers to the grid using the **+ Add Driver** button.
3.  Select the **Driver** and **Constructor** for each slot.
4.  Enter their **Grid Position**.
5.  Click **PREDICT RACE WINNER**.

## 🔧 API Endpoints

*   `GET /`: Serves the frontend interface.
*   `GET /drivers`: Returns a list of available drivers.
*   `GET /constructors`: Returns a list of available constructors.
*   `GET /locations`: Returns a list of available circuits.
*   `POST /predict`: Accepts a JSON payload of driver details and returns win probabilities.

## 📂 Project Structure

*   `src/`: Source code for data processing, feature engineering, and modeling.
*   `data/`: Directory for raw and processed data.
*   `static/`: HTML/CSS/JS assets for the frontend.
*   `app.py`: Main FastAPI application entry point.
*   `Dockerfile`: Configuration for Docker deployment.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
