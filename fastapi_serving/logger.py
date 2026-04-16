import pandas as pd
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("/logs/predictions.csv")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log_prediction(timestamp: datetime, input_data: dict, prediction: int, model_version: str):
    record = {
        "timestamp": timestamp,
        **input_data,
        "prediction": prediction,
        "model_version": model_version
    }
    df = pd.DataFrame([record])
    if LOG_FILE.exists():
        df.to_csv(LOG_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(LOG_FILE, index=False)