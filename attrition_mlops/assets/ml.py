import mlflow
import optuna
import numpy as np
import yaml
from dagster import asset
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from mlflow.tracking import MlflowClient

from attrition_mlops.resources.mlflow_resource import MLflowResource


def get_dataset_hash():
    """Lee el hash MD5 del .dvc para vincularlo a MLflow."""
    with open("data/attrition.csv.dvc") as f:
        meta = yaml.safe_load(f)
    return meta["outs"][0]["md5"]


@asset(group_name="ml")
def hp_optimization_study(
    process_dataset: dict,
    mlflow_resource: MLflowResource,
) -> str:
    """Ejecuta el estudio de Optuna y registra cada trial en MLflow."""
    ml = mlflow_resource.get_client()
    X = process_dataset["X"]
    y = process_dataset["y"]

    def objective(trial):
        solver = trial.suggest_categorical("solver", ["svd", "lsqr", "eigen"])
        shrinkage = None
        if solver in ["lsqr", "eigen"]:
            shrinkage = trial.suggest_categorical("shrinkage", [None, "auto"])

        with ml.start_run(nested=True, run_name=f"trial_{trial.number}"):
            ml.log_params({
                "solver": solver,
                "shrinkage": str(shrinkage)
            })

            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            scores = []
            for train_idx, val_idx in cv.split(X, y):
                model = LinearDiscriminantAnalysis(
                    solver=solver,
                    shrinkage=shrinkage
                )
                model.fit(X.iloc[train_idx], y.iloc[train_idx])
                proba = model.predict_proba(X.iloc[val_idx])[:, 1]
                scores.append(roc_auc_score(y.iloc[val_idx], proba))

            mean_auc = np.mean(scores)
            ml.log_metric("auc_roc_mean", mean_auc)
            ml.log_metric("auc_roc_std", np.std(scores))

        return mean_auc

    with ml.start_run(run_name="Optuna_Study") as run:
        ml.set_tag("dataset_hash", get_dataset_hash())

        study = optuna.create_study(direction="maximize")
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study.optimize(objective, n_trials=30)

        ml.log_params(study.best_params)
        ml.log_metric("best_auc_roc", study.best_value)

        return run.info.run_id


@asset(group_name="ml")
def best_model(
    hp_optimization_study: str,
    process_dataset: dict,
    mlflow_resource: MLflowResource,
) -> str:
    """Entrena el modelo final con los mejores params y lo registra."""
    ml = mlflow_resource.get_client()
    client = MlflowClient()
    X = process_dataset["X"]
    y = process_dataset["y"]

    run = client.get_run(hp_optimization_study)
    solver = run.data.params.get("solver", "svd")
    shrinkage = run.data.params.get("shrinkage", "None")
    shrinkage = None if shrinkage == "None" else shrinkage

    with ml.start_run(run_name="best_model") as run:
        model = LinearDiscriminantAnalysis(
            solver=solver,
            shrinkage=shrinkage
        )
        model.fit(X, y)

        proba = model.predict_proba(X)[:, 1]
        auc = roc_auc_score(y, proba)

        ml.log_params({"solver": solver, "shrinkage": str(shrinkage)})
        ml.log_metric("auc_roc", auc)
        ml.set_tag("dataset_hash", get_dataset_hash())

        ml.sklearn.log_model(
            model,
            artifact_path="model",
            registered_model_name=mlflow_resource.model_name
        )

        return run.info.run_id


@asset(group_name="ml")
def promote_model(
    best_model: str,
    mlflow_resource: MLflowResource,
):
    """Compara con el champion actual y promueve si es mejor."""
    mlflow_resource.get_client()
    client = MlflowClient()
    model_name = mlflow_resource.model_name

    new_run = client.get_run(best_model)
    new_auc = float(new_run.data.metrics["auc_roc"])

    try:
        champion = client.get_model_version_by_alias(model_name, "champion")
        champion_run = client.get_run(champion.run_id)
        champion_auc = float(champion_run.data.metrics["auc_roc"])
    except Exception:
        champion_auc = 0.0

    versions = client.search_model_versions(f"name='{model_name}'")
    latest_version = max(int(v.version) for v in versions)

    if new_auc > champion_auc:
        client.set_registered_model_alias(model_name, "champion", latest_version)
        print(f"Nuevo champion: v{latest_version} con AUC {new_auc:.4f}")
    else:
        print(f"Champion actual se mantiene (AUC {champion_auc:.4f} >= {new_auc:.4f})")