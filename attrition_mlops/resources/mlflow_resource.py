import mlflow
from dagster import ConfigurableResource

class MLflowResource(ConfigurableResource):
    tracking_uri: str
    experiment: str
    model_name: str

    def get_client(self):
        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_experiment(self.experiment)
        return mlflow