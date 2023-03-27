import json
import os
from typing import List, Optional
from loguru import logger

from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic.dataclasses import dataclass

from mlversion import VersionHandler
from mlversion._artifacts import Artifact, ARTIFACT_TYPES, load_artifact
from mlversion._utils import get_dirname


@dataclass
class ArtifactSubGroup:
    label: str
    parent_dir: str
    path: Optional[str] = None
    artifacts: List[Artifact] = Field(default_factory=list)

    def __post_init__(self):
        self.set_path(self.parent_dir, self.label)
        self.update()

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
                "To use the method 'add_artifact' of and object of the class "
                f"{self.__class__.__name__}, you must pass an 'Artifact' object."
            )
        return self

    def remove_artifact(self, label: str):
        self._remove_artifact_attribute(label)
        self._remove_artifact_from_list(label)

    def update_artifacts_paths(self):
        new_parent_dir = os.path.join(self.parent_dir, self.label)
        for art in self.artifacts:
            art.set_path(new_parent_dir, art.label )

    def set_path(self, parent_dir, label):
        self.path = os.path.join(parent_dir, label)

    def update(self):
        if not isinstance(self.artifacts, FieldInfo):
            for elem in self.artifacts:
                self._remove_artifact_attribute(elem.label)
                setattr(self, elem.label, elem)

            self.update_artifacts_paths()

    def _add_artifact(self, artifact):
        self.artifacts.append(artifact)
        self.update()

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
        self.set_path(self.parent_dir, self.label)
        self.update()

    class Config:
        arbitrary_types_allowed = True

    def save(self):
        if not isinstance(self.subgroups, FieldInfo):
            for subgroup in self.subgroups:
                subgroup.save()

        return self

    @classmethod
    def load(cls, label: str, parent_dir: str):
        group = ArtifactGroup(label=label, parent_dir=parent_dir)
        path = os.path.join(parent_dir, label)
        for label in os.listdir(path):
            subgroup_path = os.path.join(path, label)
            subgroup = cls._load_subgroup(subgroup_path)
            group.add_subgroup(subgroup)
        return group

    def add_subgroup(self, subgroup: ArtifactSubGroup, overwrite=False):
        if isinstance(subgroup, ArtifactSubGroup):
            if hasattr(self, subgroup.label) and not overwrite:
                raise ExistingAttributeError(self, subgroup.label)
            subgroup = self._set_subgroup_to_be_added(subgroup=subgroup)
            self._add_subgroup(subgroup)

        else:
            raise TypeError(
                "To use the method 'add_subgroup' of and object of the class "
                f"{self.__class__.__name__}, you must pass an 'ArtifactSubGroup' object."
            )
        return self

    def create_subgroup():
        pass

    def remove_subgroup(self, label: str) -> None:
        self._remove_subgroup_attribute(label)
        self._remove_subgroup_from_list(label)

    def set_path(self, parent_dir, label):
        self.path = os.path.join(parent_dir, label)

    def update(self):
        if not isinstance(self.subgroups, FieldInfo):
            for elem in self.subgroups:
                self._remove_subgroup_attribute(elem.label)
                setattr(self, elem.label, elem)

    def _remove_subgroup_attribute(self, label: str) -> None:
        if hasattr(self, label):
            delattr(self, label)

    def _remove_subgroup_from_list(self, label: str) -> None:
        self.subgroups = [elem for elem in self.subgroups if elem.label != label]

    def _set_subgroup_to_be_added(self, subgroup=None, label=None, artifacts=None):
        subgroup_passed = subgroup is not None
        label_passed = label is not None
        artifacts_passed = artifacts is not None
        new_parent_dir = self.path

        if subgroup_passed and (not label_passed) and (not artifacts_passed):
            label = subgroup.label
            artifacts = subgroup.artifacts

        if subgroup_passed and (label_passed or artifacts_passed):
            raise IncompatibleArgumentsError("If you pass and subgroup, you cannot pass the artifacts")
        
        for art in artifacts:
            art.set_path(os.path.join(new_parent_dir, label), art.label)

        return ArtifactSubGroup(
            label=label,
            parent_dir=new_parent_dir,
            artifacts=artifacts,
        )

    def _add_subgroup(self, subgroup):
        self.subgroups.append(subgroup)
        self.update()

    @classmethod
    def _load_subgroup(cls, subgroup_path: str):
        if not os.path.isdir(subgroup_path):
            raise NotADirectoryError("'{subgroup_path}' is not a valid artifact path")
        parent_dir = os.path.dirname(subgroup_path)
        label = get_dirname(subgroup_path)
        subgroup = ArtifactSubGroup.load(label, parent_dir)
        return subgroup


class ArtifactHandler:
    def __init__(self, path):
        self.path = path
        self._version_handler = VersionHandler(self.path)
        self.data: ArtifactGroup = self._set_data()

    def update_versions(self):
        self._version_handler.update()

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
