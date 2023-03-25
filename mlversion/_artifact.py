from __future__ import annotations
from abc import ABC, abstractmethod

import pandas as pd

from mlversion._version_handler import VersionHandler

# from basix.classes import validate_constructor_args
# @validate_constructor_args
    # def _validate_artifact_group(self, artifact_group):
    #     if artifact_group not in ARTIFACT_TYPES:
    #         raise ArtifactTypeNotAllowedError(artifact_group)
    #     return artifact_group

# class ArtifactTypeNotAllowedError(Exception):
#     def __init__(self, artifact_group):
#         super().__init__(
#             f"'{artifact_group}' is not allowed. Recognized artifact types are "
#             f"{ARTIFACT_TYPES}."
#         )



ARTIFACT_GROUPS = [
    "data",
    "estimator",
    "transformer",
]


class Artifact(ABC):
    def __init__(self):
        pass

    @property
    @abstractmethod
    def artifact_group(self):
        pass

    @property
    @abstractmethod
    def artifact_type(self):
        pass

    @property
    @abstractmethod
    def label(self):
        pass

    @property
    @abstractmethod
    def content(self):
        pass

    @abstractmethod
    def save(self) -> None:
        pass

    @abstractmethod
    def load(self, path: str) -> Artifact:
        pass


class CSVArtifact(Artifact):
    artifact_group = "data"
    artifact_type = pd.DataFrame

    def __init__(self, version_handler: VersionHandler, label: str, content: CSVArtifact.artifact_type):
        self._artifact_group = "data"
        self._label = label
        self.version_handler = version_handler
        self.content = content

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    def save(self):
        pass

    def load(self, path):
        pass
    