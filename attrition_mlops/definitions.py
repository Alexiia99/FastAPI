import yaml
from dagster import Definitions, load_assets_from_modules, define_asset_job, AssetSelection

from attrition_mlops.assets import data, ml
from attrition_mlops.resources.mlflow_resource import MLflowResource

# Cargar configuración
with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Cargar todos los assets de los módulos data y ml
all_assets = load_assets_from_modules([data, ml])

# Definir el job que ejecuta todo el pipeline
full_pipeline_job = define_asset_job(
    name="full_pipeline_job",
    selection=AssetSelection.all()
)

# Punto de entrada de Dagster
defs = Definitions(
    assets=all_assets,
    resources={
        "mlflow_resource": MLflowResource(
            tracking_uri=config["mlflow"]["tracking_uri"],
            experiment=config["mlflow"]["experiment"],
            model_name=config["mlflow"]["model_name"],
        )
    },
    jobs=[full_pipeline_job]
)