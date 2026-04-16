from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import pandas as pd
from .predictor import Predictor
from .schemas import PredictionRequest, PredictionResponse
from .config import APP_VERSION
from .logger import log_prediction


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.predictor = Predictor()
    print('🌸 API iniciada. Modelo listo.')
    yield
    print('🌸 API apagada.')

app = FastAPI(title='Attrition Prediction API', lifespan=lifespan)
 
# Recibe el Json, lo transformo en DataFrame y llamamos al predictor
@app.post('/predict', response_model=PredictionResponse)
async def predict(request: Request, body: PredictionRequest):
    df = pd.DataFrame([body.model_dump()])
    prediction = request.app.state.predictor.predict(df)
    label = 'Yes' if prediction[0] == 1 else 'No'

    # Monitorización
    log_prediction(
        timestamp=pd.Timestamp.now(),
        input_data=body.model_dump(),
        prediction=prediction[0],
        model_version=request.app.state.predictor.model_uri
    )

    return PredictionResponse(prediction=prediction[0], prediction_label=label)

# Verifico que está funcionando
@app.get('/health')
async def health(request: Request):
    return {'status': 'ok', 'model_loaded': request.app.state.predictor.model is not None}

# Muestra el modelo que he cargado
@app.get('/model-info')
async def model_info(request: Request):
    return {
        'model_uri': request.app.state.predictor.model_uri,
        'app_version': APP_VERSION
    }