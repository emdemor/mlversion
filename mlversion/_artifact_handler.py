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

    class Config:
        arbitrary_types_allowed = True

    def __post_init__(self):
        self._set_path(self.parent_dir, self.label)
        self._update()

    def _set_path(self, parent_dir, label):
        self.path = os.path.join(parent_dir, label)

    def _update(self):
        if not isinstance(self.artifacts, FieldInfo):
            for elem in self.artifacts:
                self.remove_artifact(elem.label)
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
            raise IncompatibleArgumentsError("If you pass and artifact, you cannot pass " "label nether the content")

        ArtifactClass = ARTIFACT_TYPES[type]

        return ArtifactClass(
            label=label,
            content=content,
            parent_dir=new_parent_dir,
        )

    def create_artifact(self, label, content, type, overwrite=False):
        if hasattr(self, label) and not overwrite:
            raise ExistingAttributeError(self, label)
        artifact = self._set_artifact_to_be_added(label=label, content=content)
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
        if hasattr(self, label):
            delattr(self, label)

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
        message = f"Attribute {attribute_name} already exists in object " f"of the class {object.__class__}."
        super().__init__(message)


class IncompatibleArgumentsError(Exception):
    pass
