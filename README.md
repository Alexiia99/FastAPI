# Predicción de Deserción Laboral — MLOps Pipeline Alexia Herrador

Pipeline completo de MLOps para predecir la deserción laboral (Attrition) usando MLflow, DVC y Dagster 🌸

## 🌼 Estructura del proyecto
```
attrition_mlops/
├── attrition_mlops/
│   ├── assets/
│   │   ├── data.py          # Assets: raw_dataset, process_dataset
│   │   └── ml.py            # Assets: hp_optimization_study, best_model, promote_model
│   ├── resources/
│   │   └── mlflow_resource.py  # Recurso MLflow configurable
│   └── definitions.py       # Punto de entrada de Dagster
├── data/
│   └── attrition.csv.dvc    # Puntero DVC (no el CSV)
├── config.yaml              # Configuración del pipeline
├── launch_runs.py           # Script para lanzar múltiples runs
└── pyproject.toml
```

## 🌼 Explicación de qué hace cada archivo

### `config.yaml`
Panel de control del pipeline. Centraliza toda la configuración (ruta del dataset, parámetros de MLflow y de Optuna) para que nunca haya que tocar el código para cambiar el comportamiento del pipeline.

### `data/attrition.csv.dvc`
Puntero de DVC. No contiene los datos, sino la huella digital (hash MD5) del CSV. Git versiona este archivo pequeño en lugar del CSV completo. Combinado con `git checkout`, permite recuperar exactamente los datos de cualquier experimento pasado.

### `attrition_mlops/resources/mlflow_resource.py`
Recurso compartido de MLflow. Define la conexión con el servidor de MLflow (URL, experimento, nombre del modelo) una sola vez. Dagster lo inyecta automáticamente en todos los assets que lo necesitan.

### `attrition_mlops/assets/data.py`
Contiene los dos primeros assets del pipeline:
- `raw_dataset`: carga el CSV desde disco y lo devuelve como DataFrame.
- `process_dataset`: elimina columnas inútiles (IDs y columnas constantes), convierte la variable objetivo Attrition de Yes/No a 1/0, y codifica las columnas categóricas con LabelEncoder.

### `attrition_mlops/assets/ml.py`
Contiene los tres assets de Machine Learning:
- `hp_optimization_study`: ejecuta un estudio de Optuna con 30 trials. Cada trial prueba una combinación de hiperparámetros de LDA evaluada con StratifiedKFold de 5 folds. Cada trial se registra como nested run en MLflow dentro de un run padre llamado `Optuna_Study`.
- `best_model`: recupera los mejores hiperparámetros del estudio, entrena el modelo final con todos los datos y lo registra en el Model Registry de MLflow como una nueva versión de `AttritionModel`.
- `promote_model`: compara el AUC-ROC del nuevo modelo con el del modelo actual con alias `champion`. Si el nuevo es mejor, le asigna el alias. Si no, el champion se mantiene.

### `attrition_mlops/definitions.py`
Punto de entrada de Dagster. Carga todos los assets, registra el recurso MLflow con los valores del `config.yaml` y define el job `full_pipeline_job` que ejecuta el pipeline completo.

### `launch_runs.py`
Script que ejecuta el pipeline completo 3 veces de forma programática con diferentes configuraciones, demostrando cómo lanzar barridos de experimentos automáticos sin intervención manual.

### `pyproject.toml`
Configuración del proyecto. Incluye la sección `[tool.dagster]` que indica a Dagster dónde encontrar el punto de entrada al ejecutar `dagster dev`.



## 🌼 Requisitos

- Python 3.10+
- uv (gestor de paquetes)

## 🌼 Instalación
```bash
git clone <url-del-repo>
cd attrition_mlops
uv sync
source .venv/bin/activate
```

Descargar los datos con DVC:
```bash
dvc pull
```

## 🌼 Ejecución

Necesitas tres terminales.

**🌼 Terminal 1 — MLflow:**
```bash
mlflow ui
```

**🌼 Terminal 2 — Dagster:**
```bash
dagster dev
```

**🌼 Terminal 3 — Lanzar runs:**
```bash
python launch_runs.py
```

- MLflow UI: http://localhost:5000
- Dagster UI: http://localhost:3000

## 🌼 Pipeline

El pipeline consta de 5 assets ejecutados en orden:

1. **`raw_dataset`** — Carga los datos crudos desde `data/attrition.csv`
2. **`process_dataset`** — Limpieza, encoding de variables categóricas y separación en X e y
3. **`hp_optimization_study`** — Optimización de hiperparámetros con Optuna (30 trials) + Cross-Validation (StratifiedKFold, 5 folds). Cada trial se registra como nested run en MLflow
4. **`best_model`** — Entrena el modelo final (LDA) con los mejores hiperparámetros y lo registra en el Model Registry de MLflow
5. **`promote_model`** — Compara el nuevo modelo con el champion actual por AUC-ROC y lo promueve si es mejor

## 🌼 Versionado de datos con DVC

El dataset tiene dos versiones versionadas con DVC:

| Versión | Filas | Commit |
|---------|-------|--------|
| v1 | 900 | `0c140b8` |
| v2 | 1323 | `e22638f` |

Para cambiar entre versiones:
```bash
# Volver a v1
git checkout 0c140b8 -- data/attrition.csv.dvc
dvc checkout

# Volver a v2
git checkout main -- data/attrition.csv.dvc
dvc checkout
```
## 🌼Problemas que he tenido con el versionado

En un primer lugar intenté conectarlo a google drive para controlar y guardar ahí el versionado pero, al no ser posible por temas de permisos,como solución configuré un remoto local con (`~/dvc-remote`) que cumple la función de simular el trabajo en equipo y el versionado fuera de git.


## 🌼 Configuración

El fichero `config.yaml` permite parametrizar el pipeline:
```yaml
data:
  path: "data/attrition.csv"

mlflow:
  tracking_uri: "http://localhost:5000"
  experiment: "Attrition_Prediction"
  model_name: "AttritionModel"

optuna:
  n_trials: 30
  cv_splits: 5
```

##  🌼 Modelo

Se usa **Linear Discriminant Analysis (LDA)** de scikit-learn. Los hiperparámetros optimizados son:

- `solver`: svd, lsqr o eigen
- `shrinkage`: None o auto (solo para lsqr y eigen)

La métrica de evaluación es **AUC-ROC** calculada con StratifiedKFold de 5 folds.