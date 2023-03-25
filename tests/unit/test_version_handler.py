import os
from loguru import logger

import pytest
from mlversion import ModelVersion, VersionHandler


def test_model_version(model_version):
    ...


def test_version_handler(version_handler):
    ...


def test_version_handler_init(version_handler, models_path):
    version_handler.init()
    assert os.path.exists(os.path.join(models_path, "version=0.0.0dev0"))

