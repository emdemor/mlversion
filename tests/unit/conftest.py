import shutil
import pandas as pd

import pytest
from basix import files
from sklearn.linear_model import LinearRegression

from mlversion import ModelVersion, VersionHandler
from mlversion._artifacts import CSVArtifact, BinaryArtifact


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
    artifact = CSVArtifact(
        label="train", content=df, parent_dir="workdir/test/data/"
    )
    return artifact

@pytest.fixture()
def bin_artifact():
    df = pd.DataFrame([[0, 10], [1, 20]], columns=["x", "y"])
    estimator = LinearRegression()
    estimator.fit(df[["x"]], df["y"])
    artifact = BinaryArtifact(
        label="linear_regression", content=estimator, parent_dir="workdir/test/models/"
    )
    return artifact
    
@pytest.fixture()
def model_version(start_version_string):
    model_version = ModelVersion(start_version_string)
    return model_version

@pytest.fixture()
def version_handler(models_path):
    version_handler = VersionHandler(models_path)
    return version_handler
