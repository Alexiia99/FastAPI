import os
import time
import pandas as pd
from datetime import datetime
from evidently import Report
from evidently.presets import DataDriftPreset, DataSummaryPreset
from evidently.metrics import ValueDrift, DriftedColumnsCount
from evidently.ui.workspace import Workspace

PREDICTIONS_LOG = os.getenv("PREDICTIONS_LOG", "/logs/predictions.csv")
REFERENCE_DATA  = os.getenv("REFERENCE_DATA", "/app/data/attrition_v1.csv")
WORKSPACE_DIR   = os.getenv("WORKSPACE_DIR", "/workspace")
DAGSTER_URL     = os.getenv("DAGSTER_URL", "http://dagster:3000")
CHECK_INTERVAL  = int(os.getenv("CHECK_INTERVAL", "120"))

FEATURE_COLS = ["Age", "MonthlyIncome", "DistanceFromHome", "YearsAtCompany", "TotalWorkingYears"]

# Para no crear un proyecto cada vez que arranca
def get_or_create_project(workspace: Workspace, name: str):
    for project in workspace.list_projects():
        if project.name == name:
            return project
    project = workspace.create_project(name)
    project.description = "Monitorización del modelo de attrition"
    project.save()
    return project


# Construye el reporte y realiza un snapshot con los resultados
def build_report(reference_df: pd.DataFrame, production_df: pd.DataFrame):
    report = Report(metrics=[
        DataDriftPreset(columns=FEATURE_COLS),
        DataSummaryPreset(columns=FEATURE_COLS),
        ValueDrift(column="Age"),
        ValueDrift(column="MonthlyIncome"),
        DriftedColumnsCount(),
    ])
    snapshot = report.run(
        reference_data=reference_df[FEATURE_COLS],
        current_data=production_df[FEATURE_COLS],
    )
    return snapshot

# Este método lee el snapshot y revisa si hay cambios (Drifts)
def drift_detected(snapshot) -> bool:
    results = snapshot.dict()
    for metric in results["metrics"]:
        if "DriftedColumnsCount" in metric.get("metric_name", ""):
            drifted = metric["value"]["count"]
            share = metric["value"]["share"]
            print(f"   Columnas con drift: {drifted} ({share*100:.0f}%)")
            return drifted > 0
    return False

# Es el bucle de monitoreo, carga los datos de referencia y cada va generando reportes de las predicciones
def run_monitoring():
    print(f"🌸 Monitor iniciado — comprobando cada {CHECK_INTERVAL}s")

    while not os.path.exists(REFERENCE_DATA):
        print("🌸 Esperando datos de referencia...")
        time.sleep(10)

    reference_df = pd.read_csv(REFERENCE_DATA)
    print(f"🌸 Datos de referencia cargados: {len(reference_df)} filas")

    workspace = Workspace(WORKSPACE_DIR)
    project = get_or_create_project(workspace, "attrition_monitoring")

    while True:
        try:
            if not os.path.exists(PREDICTIONS_LOG):
                print("🌸 Sin predicciones todavía...")
            else:
                production_df = pd.read_csv(PREDICTIONS_LOG)
                if len(production_df) < 10:
                    print(f"🌸 Solo {len(production_df)} predicciones — mínimo 10")
                else:
                    print(f"🌸 Generando report con {len(production_df)} predicciones...")
                    snapshot = build_report(reference_df, production_df)
                    workspace.add_run(project.id, snapshot)

                    if drift_detected(snapshot):
                        print(f"🌸  [{datetime.now().strftime('%H:%M:%S')}] DRIFT DETECTADO")
                        print("   Revisa el dashboard en http://localhost:8001")
                    else:
                        print(f"🌸 [{datetime.now().strftime('%H:%M:%S')}] Sin drift")

        except Exception as e:
            print(f"🌸 Error en monitorización: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        run_monitoring()
    except Exception as e:
        import traceback
        print(f"🌸 Error fatal en monitor: {e}")
        traceback.print_exc()
        time.sleep(9999)