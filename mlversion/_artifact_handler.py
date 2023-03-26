import os
from typing import List, Optional
from loguru import logger

from pydantic import Field
from pydantic.fields import FieldInfo
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
        if not isinstance(self.artifacts,FieldInfo):
            for elem in self.artifacts:
                self.remove(elem.label)
                setattr(self, elem.label, elem)

    def add(self, artifact: Artifact, overwrite=False):
        if isinstance(artifact, Artifact):
            if hasattr(self, artifact.label) and not overwrite:
                raise ExistingAttributeError(self, artifact.label)
            self.artifacts.append(artifact)
            self._update()
        else:
            raise TypeError(
                "To use the method 'add' of and object of the class "
                f"{self.__class__.__name__}, you must pass an 'Artifact' object."
            )
        return self

    def remove(self, label: str):
        if hasattr(self, label):
            delattr(self, label)

    def save(self):
        pass


    # @classmethod
    # def load(cls, label: str, parent_dir: str):
    #     for label in os.listdir(parent_dir):
    #         artifact_parent_dir = os.path.join(parent_dir, label)
    #         artifact = Artifact.load(artifact_parent_dir)

    #         match = self._version_dir_pattern_regex.search(subdir)
    #         if match:
    #             version_str = match.group(1)
    #             version = ModelVersion(version_str)
    #             self.history.append(version)
    #             if self._check_if_new_version_is_greater(self.latest_version, version):
    #                 self.latest_version = version
    #         else:
    #             raise vs.InvalidVersion(f"'{subdir} is not a valid version.")

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
