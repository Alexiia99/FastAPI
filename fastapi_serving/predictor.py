import mlflow
import mlflow.sklearn
import pandas as pd
from .config import MODEL_URI, MLFLOW_TRACKING_URI

# Cargo el modelo desde MLFlow solo una vez al iniciar.
class Predictor:
    def __init__(self):
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        self.model = mlflow.sklearn.load_model(MODEL_URI)
        self.model_uri = MODEL_URI
        print(f'Modelo cargado desde: {MODEL_URI}')

    # Para hacer una predicción, se pasa un DataFrame y devuelve el resultado
    def predict(self, data: pd.DataFrame) -> list:
        return self.model.predict(data).tolist()