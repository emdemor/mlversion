import shutil

import pytest
from basix import files

from mlversion import ModelVersion, VersionHandler


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
def model_version(start_version_string):
    model_version = ModelVersion(start_version_string)
    return model_version

@pytest.fixture()
def version_handler(models_path):
    version_handler = VersionHandler(models_path)
    return version_handler
