import os
import shutil
from typing import Literal

import pytest
from loguru import logger
from packaging import version as vs
from basix import files

from mlversion import ModelVersion, VersionHandler, ExistingVersionError


def test_model_version(model_version: ModelVersion):
    ...


def test_version_handler(version_handler: VersionHandler):
    ...


def test_version_handler_init(version_handler: VersionHandler, models_path: str):
    version_handler.init()
    assert os.path.exists(os.path.join(models_path, "version=0.0.0dev0"))


def test_version_handler_add_new_version(version_handler: VersionHandler, models_path: str):
    new_version = "0.0.1"
    version_handler.add_new_version(new_version)
    assert os.path.exists(os.path.join(models_path, f"version={new_version}"))


def test_version_handler_add_invalid_new_version(version_handler: VersionHandler, models_path: str):
    invalid_version = "0.0.1.beta1"

    with pytest.raises(vs.InvalidVersion) as exception:  
        version_handler.add_new_version(invalid_version)


def test_version_handler_add_duplicated_new_version(version_handler: VersionHandler, models_path: str):
    new_version = "0.0.2"
    version_handler.add_new_version(new_version)

    with pytest.raises(ExistingVersionError) as exception:  
        version_handler.add_new_version(new_version)


def test_version_handler_get_versions_invalid(version_handler: VersionHandler, models_path: str):
    invalid_version = "0.0.1.beta2"
    files.make_directory(os.path.join(models_path, f"version={invalid_version}"))
    with pytest.raises(vs.InvalidVersion) as exception:  
        version_handler._get_versions()
    shutil.rmtree(os.path.join(models_path, f"version={invalid_version}"))
    

def test_check_if_new_version_is_greater(version_handler: VersionHandler):
    assert version_handler._check_if_new_version_is_greater("0.0.1", "0.0.2")
    assert version_handler._check_if_new_version_is_greater("0.0.1", "0.1.0")
    assert version_handler._check_if_new_version_is_greater("0.0.1", "1.0.0")
    assert version_handler._check_if_new_version_is_greater("0.1.0", "1.0.0")
    assert version_handler._check_if_new_version_is_greater("1.0.0", "2.0.0")
    assert version_handler._check_if_new_version_is_greater("0.0.1", "0.0.1dev1")
    assert version_handler._check_if_new_version_is_greater("0.0.1dev1", "0.0.1dev2")
    assert not version_handler._check_if_new_version_is_greater("0.0.2", "0.0.1")
    assert not version_handler._check_if_new_version_is_greater("0.1.0", "0.0.1")
    assert not version_handler._check_if_new_version_is_greater("1.0.0", "0.0.1")
    assert not version_handler._check_if_new_version_is_greater("1.0.0", "0.1.0")
    assert not version_handler._check_if_new_version_is_greater("2.0.0", "1.0.0")
    assert not version_handler._check_if_new_version_is_greater("0.0.1dev1", "0.0.1")
    assert not version_handler._check_if_new_version_is_greater("0.0.1dev2", "0.0.1dev1")
    assert not version_handler._check_if_new_version_is_greater("0.0.1", "0.0.1")
    assert not version_handler._check_if_new_version_is_greater("0.1.0", "0.1.0")
    assert not version_handler._check_if_new_version_is_greater("1.0.0", "1.0.0")
    assert version_handler._check_if_new_version_is_greater(None, "1.0.0")
    assert not version_handler._check_if_new_version_is_greater("1.0.0", None)
    with pytest.raises(TypeError):
        version_handler._check_if_new_version_is_greater(None, None)
