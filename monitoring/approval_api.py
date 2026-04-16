import os
import requests
import yaml
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

DAGSTER_URL = os.getenv("DAGSTER_URL", "http://dagster:3000")
PREDICTIONS_LOG = os.getenv("PREDICTIONS_LOG", "/logs/predictions.csv")
CONFIG_PATH = os.getenv("CONFIG_PATH", "/app/config.yaml")


def trigger_retraining():
    with open(CONFIG_PATH) as f:
        run_config = yaml.safe_load(f)

    response = requests.post(
        f"{DAGSTER_URL}/graphql",
        json={
            "query": """
                mutation LaunchRun($runConfig: RunConfigData!) {
                    launchRun(executionParams: {
                        selector: {
                            jobName: "full_pipeline_job"
                            repositoryName: "__repository__"
                            repositoryLocationName: "attrition_mlops.definitions"
                        }
                        runConfigData: $runConfig
                    }) {
                        __typename
                        ... on LaunchRunSuccess {
                            run { runId }
                        }
                        ... on PythonError {
                            message
                        }
                    }
                }
            """,
            "variables": {"runConfig": run_config}
        },
        timeout=10
    )
    run_id = response.json()["data"]["launchRun"]["run"]["runId"]
    return run_id


def clear_predictions_log():
    if os.path.exists(PREDICTIONS_LOG):
        os.remove(PREDICTIONS_LOG)
        print("🌼 Log de predicciones limpiado")


@app.get("/approve-retraining", response_class=HTMLResponse)
def approve():
    try:
        run_id = trigger_retraining()
        clear_predictions_log()
        return f"""
        <html><body>
        <h2>🌼 Reentrenamiento aprobado</h2>
        <p>Pipeline lanzado — run_id: {run_id}</p>
        <p><a href="http://localhost:3000">Ver en Dagster</a></p>
        </body></html>
        """
    except Exception as e:
        return f"<html><body><h2>🌼 Error</h2><p>{e}</p></body></html>"


@app.get("/reject-retraining", response_class=HTMLResponse)
def reject():
    print("🌼 Reentrenamiento rechazado por el usuario")
    return """
    <html><body>
    <h2>🌼 Reentrenamiento rechazado</h2>
    <p>No se realizará ningún cambio en el modelo.</p>
    </body></html>
    """


@app.get("/health")
def health():
    return {"status": "ok"}