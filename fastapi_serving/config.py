import os
from dotenv import load_dotenv

load_dotenv()

MODEL_URI = os.getenv("MODEL_URI", "models:/AttritionModel@champion")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")