import pytest
from mlversion import ModelVersion, VersionHandler


@pytest.fixture()
def start_version_string():
    return "0.0.0"

@pytest.fixture()
def models_path():
    return "workdir/models"

@pytest.fixture()
def model_version(start_version_string):
    model_version = ModelVersion(start_version_string)
    return model_version

@pytest.fixture()
def version_handler(models_path):
    version_handler = VersionHandler(models_path)
    return version_handler
