from typing import List

from pydantic import Field
from pydantic.dataclasses import dataclass

from mlversion import VersionHandler
from mlversion._artifacts import Artifact


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
            label="data",
            artifacts_subgroups=[
                ArtifactSubGroup(label="raw"),
                ArtifactSubGroup(label="interim"),
                ArtifactSubGroup(label="transformed"),
                ArtifactSubGroup(label="predicted"),
            ],
        )
