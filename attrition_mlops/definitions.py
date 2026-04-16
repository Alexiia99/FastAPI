import os
import yaml
from dagster import Definitions, load_assets_from_modules, define_asset_job, AssetSelection

from attrition_mlops.assets import data, ml
from attrition_mlops.resources.mlflow_resource import MLflowResource

# Cargar configuración
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# La variable de entorno sobreescribe el config.yaml
tracking_uri = os.getenv("MLFLOW_TRACKING_URI", config["mlflow"]["tracking_uri"])

all_assets = load_assets_from_modules([data, ml])

full_pipeline_job = define_asset_job(
    name="full_pipeline_job",
    selection=AssetSelection.all()
)

defs = Definitions(
    assets=all_assets,
    resources={
        "mlflow_resource": MLflowResource(
            tracking_uri=tracking_uri,
            experiment=config["mlflow"]["experiment"],
            model_name=config["mlflow"]["model_name"],
        )
    },
    jobs=[full_pipeline_job]
)