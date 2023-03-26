from __future__ import annotations
import os
from abc import ABC, abstractmethod
from typing import Any, Optional

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
        self.path = os.path.join(parent_dir, label+".csv")

    @abstractmethod
    def save(self) -> Artifact:
        pass

    @abstractmethod
    def load(self, path):
        pass


class CSVArtifact(Artifact):
    type: str = "csv_table"
    def __init__(self, label: str, content: pd.DataFrame, parent_dir: str):
        super().__init__(label=label, content=content, type=self.type, parent_dir=parent_dir, path=self.path)

    def __repr__(self):
        return _get_dataframe_representation(self.content)

    def __str__(self):
        return _get_dataframe_representation(self.content)
    
    def _set_path(self, parent_dir, label):
        self.path = os.path.join(parent_dir, label+".csv")
    
    def save(self) -> CSVArtifact:
        files.make_directory(self.parent_dir)
        self.content.to_csv(self.path, index=False)
        return self

    def load(self, path: Optional[str]=None):
        if path is None:
            path = self.path
        return pd.read_csv(path)


class BinaryArtifact(Artifact):
    type: str = "model_binary"
    def __init__(self, label: str, content: Any, parent_dir: str):
        super().__init__(label=label, content=content, type=self.type, parent_dir=parent_dir, path=self.path)
    
    def save(self) -> BinaryArtifact:
        files.make_directory(self.parent_dir)
        save_bin(self.content, self.path)
        return self

    def load(self, path: Optional[str]=None):
        if path is None:
            path = self.path
        return load_bin(path)
