from __future__ import annotations
from abc import ABC, abstractmethod

from mlversion._version_handler import VersionHandler

# from basix.classes import validate_constructor_args
# @validate_constructor_args
    # def _validate_artifact_type(self, artifact_type):
    #     if artifact_type not in ARTIFACT_TYPES:
    #         raise ArtifactTypeNotAllowedError(artifact_type)
    #     return artifact_type

# class ArtifactTypeNotAllowedError(Exception):
#     def __init__(self, artifact_type):
#         super().__init__(
#             f"'{artifact_type}' is not allowed. Recognized artifact types are "
#             f"{ARTIFACT_TYPES}."
#         )



ARTIFACT_TYPES = [
    "data",
    "estimator",
    "transformer",
]


class Artifact(ABC):
    def __init__(self):
        pass

    @property
    @abstractmethod
    def artifact_type(self):
        pass

    @property
    @abstractmethod
    def label(self):
        pass

    @abstractmethod
    def save(self) -> None:
        pass

    @abstractmethod
    def load(self, path: str) -> Artifact:
        pass


class CSVArtifact(Artifact):
    artifact_type = "data"

    def __init__(self, version_handler: VersionHandler, label: str):
        self._artifact_type = "data"
        self._label = label
        self.version_handler = version_handler

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
    