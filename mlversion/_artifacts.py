from __future__ import annotations
import os
import json
from abc import ABC, abstractmethod
from typing import Any, Optional

from loguru import logger
import pandas as pd
from basix import files
from pydantic.dataclasses import dataclass

from mlversion._utils import get_dataframe_representation, save_bin, load_bin, get_dirname
from mlversion.errors import IncompatibleArtifactTypeError


@dataclass
class Artifact(ABC, object):
    label: str
    content: Any
    type: str
    parent_dir: str
    path: Optional[str] = None

    def __post_init__(self):
        self.set_path(self.parent_dir, self.label)

    def set_path(self, parent_dir, label):
        setattr(self, "parent_dir", parent_dir)
        setattr(self, "path", os.path.join(parent_dir, label))

    def get(self):
        return self.content

    @abstractmethod
    def save(self) -> Artifact:
        pass

    @abstractmethod
    def load(self, path):
        pass

    def _save_metadata(self):
        metadata = {"type": self.type}
        metadata_path = os.path.join(self.path, "metadata")
        with open(metadata_path, "w") as file:
            json.dump(metadata, file)

    @classmethod
    def _load_metadata(cls, path):
        metadata_path = os.path.join(path, "metadata")

        with open(metadata_path, "r") as file:
            metadata = json.loads(file.read())
        if metadata["type"] != cls.type:
            raise IncompatibleArtifactTypeError(cls.type, metadata["type"])
        return metadata


class CSVArtifact(Artifact):
    type: str = "csv"

    def __init__(self, label: str, content: pd.DataFrame, parent_dir: str):
        super().__init__(label=label, content=content, type=self.type, parent_dir=parent_dir, path=self.path)

    def __repr__(self):
        return get_dataframe_representation(self.content)

    def __str__(self):
        return get_dataframe_representation(self.content)

    def save(self) -> CSVArtifact:
        files.make_directory(self.path)
        self._save_content()
        self._save_metadata()
        return self

    def _save_content(self):
        content_filepath = os.path.join(self.path, "content")
        logger.debug(f"Saving csv artifact to {content_filepath}")
        self.content.to_csv(content_filepath, index=False)

    @classmethod
    def load(cls, label: str, parent_dir: str):
        path = os.path.join(parent_dir, label)
        if not os.path.exists(path):
            raise FileNotFoundError(f"The csv table '{path}' do not exists.")
        logger.debug(f"Loading csv artifact from {path}")
        cls._load_metadata(path)
        content = cls._load_content(path)
        return cls(label=label, content=content, parent_dir=parent_dir)

    @classmethod
    def _load_content(cls, path):
        content_path = os.path.join(path, "content")
        return pd.read_csv(content_path)


class ParquetArtifact(Artifact):
    type: str = "parquet"

    def __init__(self, label: str, content: pd.DataFrame, parent_dir: str):
        super().__init__(label=label, content=content, type=self.type, parent_dir=parent_dir, path=self.path)

    def __repr__(self):
        return get_dataframe_representation(self.content)

    def __str__(self):
        return get_dataframe_representation(self.content)

    def save(self, *args, **kwargs) -> ParquetArtifact:
        files.make_directory(self.path)
        self._save_content(*args, **kwargs)
        self._save_metadata()
        return self

    def _save_content(self, *args, **kwargs):
        content_filepath = os.path.join(self.path, "content")
        logger.debug(f"Saving csv artifact to {content_filepath}")
        self.content.to_parquet(content_filepath, index=False, *args, **kwargs)

    @classmethod
    def load(cls, label: str, parent_dir: str, *args, **kwargs):
        path = os.path.join(parent_dir, label)
        if not os.path.exists(path):
            raise FileNotFoundError(f"The csv table '{path}' do not exists.")
        logger.debug(f"Loading csv artifact from {path}")
        cls._load_metadata(path)
        content = cls._load_content(path, *args, **kwargs)
        return cls(label=label, content=content, parent_dir=parent_dir)

    @classmethod
    def _load_content(cls, path, *args, **kwargs):
        content_path = os.path.join(path, "content")
        return pd.read_parquet(content_path, *args, **kwargs)


class BinaryArtifact(Artifact):
    type: str = "binary"

    def __init__(self, label: str, content: Any, parent_dir: str):
        super().__init__(label=label, content=content, type=self.type, parent_dir=parent_dir, path=self.path)

    def save(self) -> BinaryArtifact:
        files.make_directory(self.path)
        self._save_content()
        self._save_metadata()
        return self

    def _save_content(self):
        content_filepath = os.path.join(self.path, "content")
        logger.debug(f"Saving binary artifact to {content_filepath}")
        save_bin(self.content, content_filepath)

    @classmethod
    def load(cls, label: str, parent_dir: str):
        path = os.path.join(parent_dir, label)
        if not os.path.exists(path):
            raise FileNotFoundError(f"The binary '{path}' do not exists.")
        logger.debug(f"Loading binary artifact from {path}")
        cls._load_metadata(path)
        content = cls._load_content(path)
        return cls(label=label, content=content, parent_dir=parent_dir)

    @classmethod
    def _load_content(cls, path):
        content_path = os.path.join(path, "content")
        return load_bin(content_path)


def get_artifact_classes():
    return {cls.type: cls for cls in Artifact.__subclasses__()}


def load_artifact(artifact_path: str):

    if not os.path.isdir(artifact_path):
        raise NotADirectoryError("'{artifact_path}' is not a valid artifact path")

    parent_dir = os.path.dirname(artifact_path)

    label = get_dirname(artifact_path)

    metadata_path = os.path.join(artifact_path, "metadata")

    with open(metadata_path, "r") as file:
        metadata = json.loads(file.read())

    artifact_type = metadata["type"]

    ArtifactClass = ARTIFACT_TYPES[artifact_type]

    artifact = ArtifactClass.load(label, parent_dir)

    return artifact


ARTIFACT_TYPES = get_artifact_classes()
