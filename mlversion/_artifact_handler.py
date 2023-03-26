import os
from typing import List, Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from mlversion import VersionHandler
from mlversion._artifacts import Artifact


@dataclass
class ArtifactSubGroup:
    label: str
    parent_dir: str
    path: Optional[str] = None
    artifacts: List[Artifact] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    def __post_init__(self):
        self._set_path(self.parent_dir, self.label)
        self._update()

    def _set_path(self, parent_dir, label):
        self.path = os.path.join(parent_dir, label)

    def _update(self):
        for elem in self.artifacts:
            self.remove(elem.label)
            setattr(self, elem.label, elem)

    def add(self, artifact: Artifact, overwrite=False):
        if isinstance(artifact, ArtifactSubGroup):
            if hasattr(self, artifact.label) and not overwrite:
                raise ExistingAttributeError(self, artifact.label)
            self.artifacts.append(ArtifactSubGroup)
            self._update()
        else:
            raise TypeError(
                "To use the method 'add' of and object of the class "
                f"{self.__class__}, you must pass an 'ArtifactSubGroup' object."
                )

    def remove(self, label: str):
        if hasattr(self, label):
            delattr(self, label)

    @classmethod
    def load(cls):
        pass


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
            label="data",
            artifacts_subgroups=[
                ArtifactSubGroup(label="raw"),
                ArtifactSubGroup(label="interim"),
                ArtifactSubGroup(label="transformed"),
                ArtifactSubGroup(label="predicted"),
            ],
        )

class ExistingAttributeError(Exception):
    def __init__(self, object, attribute_name):
        message = (
            f"Attribute {attribute_name} already exists in object "
            f"of the class {object.__class__}."
        )
        super().__init__(message)

