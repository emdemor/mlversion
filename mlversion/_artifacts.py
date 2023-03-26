from __future__ import annotations
import os
from abc import ABC, abstractmethod
from typing import Any, Optional
import json

import pandas as pd
from basix import files
from pydantic.dataclasses import dataclass

from mlversion._utils import _get_dataframe_representation, save_bin, load_bin


@dataclass
class Artifact(ABC):
    label: str
    content: Any
    type: str
    parent_dir: str
    path: Optional[str] = None

    def __post_init__(self):
        self._set_path(self.parent_dir, self.label)

    def _set_path(self, parent_dir, label):
        self.path = os.path.join(parent_dir, label)

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
    type: str = "csv_table"

    def __init__(self, label: str, content: pd.DataFrame, parent_dir: str):
        super().__init__(label=label, content=content, type=self.type, parent_dir=parent_dir, path=self.path)

    def __repr__(self):
        return _get_dataframe_representation(self.content)

    def __str__(self):
        return _get_dataframe_representation(self.content)

    def save(self) -> CSVArtifact:
        files.make_directory(self.path)
        self._save_content()
        self._save_metadata()
        return self
    
    def _save_content(self):
        content_filepath = os.path.join(self.path, "content")
        self.content.to_csv(content_filepath, index=False)

    @classmethod
    def load(cls, label: str, parent_dir: str):
        path = os.path.join(parent_dir, label)
        if not os.path.exists(path):
            raise FileNotFoundError(f"The csv table '{path}' do not exists.")
        metadata = cls._load_metadata(path)
        content = cls._load_content(path)
        return cls(label=label, content=content, parent_dir=parent_dir)
    
    @classmethod
    def _load_content(cls, path):
        content_path = os.path.join(path, "content")
        return pd.read_csv(content_path)



class BinaryArtifact(Artifact):
    type: str = "model_binary"

    def __init__(self, label: str, content: Any, parent_dir: str):
        super().__init__(label=label, content=content, type=self.type, parent_dir=parent_dir, path=self.path)

    def save(self) -> BinaryArtifact:
        files.make_directory(self.path)
        self._save_content()
        self._save_metadata()
        return self
    
    def _save_content(self):
        content_filepath = os.path.join(self.path, "content")
        save_bin(self.content, content_filepath)

    @classmethod
    def load(cls, label: str, parent_dir: str):
        path = os.path.join(parent_dir, label)
        if not os.path.exists(path):
            raise FileNotFoundError(f"The binary '{path}' do not exists.")
        metadata = cls._load_metadata(path)
        content = cls._load_content(path)
        return cls(label=label, content=content, parent_dir=parent_dir)
    
    @classmethod
    def _load_content(cls, path):
        content_path = os.path.join(path, "content")
        return load_bin(content_path)


class IncompatibleArtifactTypeError(Exception):
    def __init__(self, expected_type, local_type):
        message = (
            f"Local artifact type {local_type} is incompatible with "
            f"the expected type {expected_type}."
        )
        super().__init__(message)
