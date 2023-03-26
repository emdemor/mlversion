import os
from typing import List, Optional

from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic.dataclasses import dataclass

from mlversion import VersionHandler
from mlversion._artifacts import Artifact, ARTIFACT_TYPES, load_artifact


@dataclass
class ArtifactSubGroup:
    label: str
    parent_dir: str
    path: Optional[str] = None
    artifacts: List[Artifact] = Field(default_factory=list)

    def __post_init__(self):
        self._set_path(self.parent_dir, self.label)
        self._update()

    class Config:
        arbitrary_types_allowed = True

    def save(self):
        if not isinstance(self.artifacts, FieldInfo):
            for artifact in self.artifacts:
                artifact.save()

        return self

    @classmethod
    def load(cls, label: str, parent_dir: str):
        subgroup = ArtifactSubGroup(label=label, parent_dir=parent_dir)
        path = os.path.join(parent_dir, label)
        for label in os.listdir(path):
            artifact_path = os.path.join(path, label)
            artifact = load_artifact(artifact_path)
            subgroup.add_artifact(artifact)
        return subgroup

    def create_artifact(self, label, content, type, overwrite=False):
        if hasattr(self, label) and not overwrite:
            raise ExistingAttributeError(self, label)
        artifact = self._set_artifact_to_be_added(label=label, content=content, type=type)
        self._add_artifact(artifact)
        return self

    def add_artifact(self, artifact: Artifact, overwrite=False):
        if isinstance(artifact, Artifact):
            if hasattr(self, artifact.label) and not overwrite:
                raise ExistingAttributeError(self, artifact.label)
            artifact = self._set_artifact_to_be_added(artifact=artifact)
            self._add_artifact(artifact)

        else:
            raise TypeError(
                "To use the method 'add' of and object of the class "
                f"{self.__class__.__name__}, you must pass an 'Artifact' object."
            )
        return self

    def remove_artifact(self, label: str):
        self._remove_artifact_attribute(label)
        self._remove_artifact_from_list(label)

    def _set_path(self, parent_dir, label):
        self.path = os.path.join(parent_dir, label)

    def _update(self):
        if not isinstance(self.artifacts, FieldInfo):
            for elem in self.artifacts:
                self._remove_artifact_attribute(elem.label)
                setattr(self, elem.label, elem)

    def _add_artifact(self, artifact):
        self.artifacts.append(artifact)
        self._update()

    def _set_artifact_to_be_added(self, artifact=None, label=None, content=None, type=None):
        artifact_passed = artifact is not None
        label_passed = label is not None
        content_passed = content is not None
        type_passed = type is not None
        new_parent_dir = self.path

        if artifact_passed and (not label_passed) and (not content_passed) and (not type_passed):
            label = artifact.label
            content = artifact.content
            type = artifact.type

        if artifact_passed and (label_passed or content_passed or type_passed):
            raise IncompatibleArgumentsError("If you pass and artifact, you cannot pass label and content")

        ArtifactClass = ARTIFACT_TYPES[type]

        return ArtifactClass(
            label=label,
            content=content,
            parent_dir=new_parent_dir,
        )

    def _remove_artifact_attribute(self, label: str) -> None:
        if hasattr(self, label):
            delattr(self, label)

    def _remove_artifact_from_list(self, label: str) -> None:
        self.artifacts = [elem for elem in self.artifacts if elem.label != label]


@dataclass
class ArtifactGroup:
    label: str
    parent_dir: str
    path: Optional[str] = None
    subgroups: List[ArtifactSubGroup] = Field(default_factory=list)

    def __post_init__(self):
        self._set_path(self.parent_dir, self.label)
        self._update()

    class Config:
        arbitrary_types_allowed = True

    def add_subgroup():
        pass

    def create_subgroup():
        pass

    def remove_subgroup(self, label: str) -> None:
        self._remove_subgroup_attribute(label)
        self._remove_subgroup_from_list(label)

    def _set_path(self, parent_dir, label):
        self.path = os.path.join(parent_dir, label)

    def _update(self):
        if not isinstance(self.subgroups, FieldInfo):
            for elem in self.subgroups:
                self._remove_subgroup_attribute(elem.label)
                setattr(self, elem.label, elem)

    def _remove_subgroup_attribute(self, label: str) -> None:
        if hasattr(self, label):
            delattr(self, label)

    def _remove_subgroup_from_list(self, label: str) -> None:
        self.subgroups = [elem for elem in self.subgroups if elem.label != label]


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
            subgroups=[
                ArtifactSubGroup(label="raw"),
                ArtifactSubGroup(label="interim"),
                ArtifactSubGroup(label="transformed"),
                ArtifactSubGroup(label="predicted"),
            ],
        )


class ExistingAttributeError(Exception):
    def __init__(self, object, attribute_name):
        message = f"Attribute {attribute_name} already exists in object " f"of the class {object.__class__}."
        super().__init__(message)


class IncompatibleArgumentsError(Exception):
    pass
