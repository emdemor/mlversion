import shutil
import pandas as pd

import pytest
from basix import files
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from mlversion import ModelVersion, VersionHandler
from mlversion._artifacts import CSVArtifact, BinaryArtifact
from mlversion._artifact_handler import ArtifactSubGroup, ArtifactGroup, ArtifactHandler


sklearn.set_config(transform_output = "pandas")


@pytest.fixture()
def start_version_string():
    return "0.0.0"


@pytest.fixture(scope="session")
def models_path():
    directory = "workdir/models"
    files.make_directory(directory)
    yield directory
    shutil.rmtree(directory, ignore_errors=True)


@pytest.fixture()
def csv_artifact():
    df = pd.DataFrame([[0, 10], [1, 12]], columns=["id", "value"])
    artifact = CSVArtifact(label="train", content=df, parent_dir="workdir/test/data/")
    return artifact


@pytest.fixture()
def bin_artifact():
    df = pd.DataFrame([[0, 10], [1, 20]], columns=["x", "y"])
    estimator = LinearRegression()
    estimator.fit(df[["x"]], df["y"])
    artifact = BinaryArtifact(label="linear_regression", content=estimator, parent_dir="workdir/test/models/")
    return artifact


@pytest.fixture()
def artifact_subgroup(csv_artifact, bin_artifact):
    artifact_subgroup = (
        ArtifactSubGroup(label="poc", parent_dir="workdir/test/")
        .add_artifact(csv_artifact)
        .add_artifact(bin_artifact)
    )
    return artifact_subgroup


@pytest.fixture()
def artifact_group(artifact_subgroup):
    artifact_group = (
        ArtifactGroup(label="clustering", parent_dir="workdir/test/")
        .add_subgroup(artifact_subgroup)
    )
    return artifact_group


@pytest.fixture()
def model_version(start_version_string):
    model_version = ModelVersion(start_version_string)
    return model_version


@pytest.fixture()
def version_handler(models_path):
    version_handler = VersionHandler(models_path)
    return version_handler

@pytest.fixture()
def artifact_handler():
    artifact_handler = ArtifactHandler(parent_dir = "workdir/handler")

    scaler = StandardScaler()
    estimator = LinearRegression()

    X_train = pd.DataFrame([[0, 10], [1, 20]], columns=["a", "b"])
    X_test = pd.DataFrame([[0, 11], [1, 21]], columns=["a", "b"])
    y_train = pd.Series([3,4])
    y_test = pd.Series([3,4])

    X_predict = pd.DataFrame([[0, 10.1], [1.1, 20.1]], columns=["a", "b"])

    scaler.fit(X_train, y_train)

    X_train_transformed = scaler.transform(X_train)
    X_test_transformed = scaler.transform(X_test)

    estimator.fit(X_train_transformed, y_train)

    artifact_handler.data.raw.create_artifact(label="X_train", content=X_train, type="csv")
    artifact_handler.data.raw.create_artifact(label="X_test", content=X_test, type="csv")
    artifact_handler.data.raw.create_artifact(label="X_predict", content=X_predict, type="csv")
    artifact_handler.data.raw.create_artifact(label="y_train", content=y_train, type="csv")
    artifact_handler.data.raw.create_artifact(label="y_test", content=y_test, type="csv")
    artifact_handler.data.transformed.create_artifact(label="X_train_transformed", content=X_train_transformed, type="parquet")
    artifact_handler.data.transformed.create_artifact(label="X_test_transformed", content=X_test_transformed, type="parquet")
    artifact_handler.models.transformers.create_artifact(label="scaler", content=scaler, type="binary")
    artifact_handler.models.estimators.create_artifact(label="estimator", content=estimator, type="binary")

    return artifact_handler