import pandas as pd
from dagster import asset
from sklearn.preprocessing import LabelEncoder

@asset(group_name="data")
def raw_dataset() -> pd.DataFrame:
    """Carga los datos crudos desde el CSV."""
    df = pd.read_csv("data/attrition.csv")
    return df

@asset(group_name="data")
def process_dataset(raw_dataset: pd.DataFrame) -> dict:
    """Limpieza, encoding y separación en X e y."""
    df = raw_dataset.copy()

    # Eliminar columnas que no aportan información
    df = df.drop(columns=["EmployeeCount", "EmployeeNumber", "Over18", "StandardHours"])

    # Convertir la variable objetivo: Yes=1, No=0
    df["Attrition"] = (df["Attrition"] == "Yes").astype(int)

    # Convertir el resto de columnas categóricas a números
    le = LabelEncoder()
    for col in df.select_dtypes(include="object").columns:
        df[col] = le.fit_transform(df[col])

    # Separar features y objetivo
    X = df.drop(columns=["Attrition"])
    y = df["Attrition"]

    return {"X": X, "y": y}