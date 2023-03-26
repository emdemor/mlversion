from loguru import logger
import numpy as np
import pandas as pd
from mlversion._artifact_handler import ArtifactGroup, ArtifactSubGroup
from mlversion._artifacts import CSVArtifact, BinaryArtifact
from sklearn.linear_model import LinearRegression


def test_csv_artifact():
    df = pd.DataFrame([[0, 10], [1, 12]], columns=["id", "value"])
    artifact = CSVArtifact(
        label="train", content=df, parent_dir="workdir/test/data/"
    ).save()
    df_imported = pd.read_csv("workdir/test/data/train")
    assert df.equals(df_imported)


def test_binary_artifact():
    expected_value = 30

    df = pd.DataFrame([[0, 10], [1, 20]], columns=["x", "y"])
    estimator = LinearRegression()
    estimator.fit(df[["x"]], df["y"])
    artifact = BinaryArtifact(
        label="linear_regression", content=estimator, parent_dir="workdir/test/models/"
    ).save()

    imported_artifact = BinaryArtifact.load(
        label="linear_regression", parent_dir="workdir/test/models/"
    )
    imported_estimator = imported_artifact.content
    prediction = imported_estimator.predict([[2]])[0]

    assert np.isclose(expected_value, prediction)

