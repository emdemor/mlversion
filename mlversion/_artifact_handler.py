from abc import ABC, abstractmethod
import os
from typing import Any, List, Optional

import pandas as pd
from loguru import logger
from pydantic import Field
from pydantic.dataclasses import dataclass
from basix import files

from mlversion import VersionHandler
from mlversion._utils import _get_dataframe_representation


@dataclass
class Artifact(ABC):
    label: str
    content: Any
    type: str
    parent_dir: str
    path: Optional[str] = None

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def load(self, path):
        pass


class CSVArtifact(Artifact):
    type: str = "csv_table"
    def __init__(self, label: str, content: pd.DataFrame, parent_dir: str):
        self._set_path(parent_dir, label)
        super().__init__(label=label, content=content, type=self.type, parent_dir=parent_dir, path=self.path)

    def __repr__(self):
        return _get_dataframe_representation(self.content)

    def __str__(self):
        return _get_dataframe_representation(self.content)
    
    def _set_path(self, parent_dir, label):
        self.path = os.path.join(parent_dir, label+".csv")
    
    def save(self):
        files.make_directory(self.parent_dir)
        self.content.to_csv(self.path, index=False)

    def load(self, path: Optional[str]=None):
        if path is None:
            path = self.path
        return pd.read_csv(path)


@dataclass
class ArtifactSubGroup:
    label: str
    artifacts: List[Artifact] = Field(default_factory=list)
    class Config:
        arbitrary_types_allowed = True


@dataclass
class ArtifactGroup:
    label: str
    artifacts_subgroups: List[ArtifactSubGroup] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    def __post_init__(self):
        self._update()

    def _update(self):
        for elem in self.artifacts_subgroups:
            setattr(self, elem.label, elem)
    
    def add(self, artifact: ArtifactSubGroup):
        if isinstance(artifact, ArtifactSubGroup):
            self.artifacts_subgroups.append(ArtifactSubGroup)
            self._update()
        else:
            raise TypeError("You must pass an 'ArtifactSubGroup' object.")


class ArtifactHandler:
    def __init__(self, path):
        self.path = path
        self._version_handler = VersionHandler(self.path)
        self.data: ArtifactGroup = self._set_data()

    def _update_versions(self):
        self._version_handler._update()

    def _set_data(self):
        return ArtifactGroup(
            label = "data",
            artifacts_subgroups = [
                ArtifactSubGroup(label="raw"),
                ArtifactSubGroup(label="interim"),
                ArtifactSubGroup(label="transformed"),
                ArtifactSubGroup(label="predicted"),
            ]
        )
