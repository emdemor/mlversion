import os
from typing import List, Optional
from loguru import logger
from distutils.dir_util import copy_tree

from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic.dataclasses import dataclass
from basix import files

from mlversion import VersionHandler
from mlversion._artifacts import Artifact, ARTIFACT_TYPES, load_artifact
from mlversion._utils import get_dirname
from mlversion.errors import ExistingAttributeError, IncompatibleArgumentsError


@dataclass
class ArtifactSubGroup:
    """
    A group of artifacts that share a parent directory.

    Parameters
    ----------
    label : str
        The label for the subgroup.
    parent_dir : str
        The path of the parent directory for the subgroup.
    path : Optional[str], default=None
        The path of the directory containing the artifacts. If not provided, it is constructed using the parent
        directory and the subgroup label.
    artifacts : List[Artifact], default=[]
        The list of artifacts in the subgroup.

    Attributes
    ----------
    label : str
        The label for the subgroup.
    parent_dir : str
        The path of the parent directory for the subgroup.
    path : Optional[str]
        The path of the directory containing the artifacts. If not provided, it is constructed using the parent
        directory and the subgroup label.
    artifacts : List[Artifact]
        The list of artifacts in the subgroup.

    Methods
    -------
    save() -> ArtifactSubGroup:
        Saves all artifacts in the subgroup.
    load(label: str, parent_dir: str) -> ArtifactSubGroup:
        Loads a subgroup of artifacts from a directory.
    create_artifact(label: str, content: Any, type: str, overwrite: bool = False) -> ArtifactSubGroup:
        Creates a new artifact in the subgroup.
    add_artifact(artifact: Artifact, overwrite: bool = False) -> ArtifactSubGroup:
        Adds an existing artifact to the subgroup.
    remove_artifact(label: str) -> ArtifactSubGroup:
        Removes an artifact from the subgroup.
    update_artifacts_paths() -> None:
        Updates the paths of all artifacts in the subgroup.
    set_path(parent_dir: str, label: str) -> None:
        Sets the path of the subgroup.
    update() -> None:
        Updates the list of artifacts in the subgroup.

    Raises
    ------
    ExistingAttributeError
        Raised when trying to create or add an artifact with a label that already exists in the subgroup.
    TypeError
        Raised when trying to add an object that is not an Artifact to the subgroup.
    IncompatibleArgumentsError
        Raised when trying to create an artifact with both an Artifact object and label/content/type arguments.

    """

    label: str
    parent_dir: str
    path: Optional[str] = None
    artifacts: List[Artifact] = Field(default_factory=list)

    def __post_init__(self):
        """
        Post-initialization step that sets the path of the subgroup and updates the list of artifacts.
        """
        self.set_path(self.parent_dir, self.label)
        self.update()

    class Config:
        """
        Pydantic configuration.
        """

        arbitrary_types_allowed = True

    def save(self) -> "ArtifactSubGroup":
        """
        Saves all artifacts in the subgroup.

        Returns
        -------
        ArtifactSubGroup
            The updated subgroup.
        """
        if not isinstance(self.artifacts, FieldInfo):
            for artifact in self.artifacts:
                artifact.save()

        return self

    @classmethod
    def load(cls, label: str, parent_dir: str) -> "ArtifactSubGroup":
        """
        Loads an `ArtifactSubGroup` object from a directory.

        Parameters
        ----------
        cls : type
            The class.
        label : str
            The label of the subgroup.
        parent_dir : str
            The path to the parent directory of the subgroup.

        Returns
        -------
        ArtifactSubGroup
            The `ArtifactSubGroup` object.
        """
        subgroup = ArtifactSubGroup(label=label, parent_dir=parent_dir)
        path = os.path.join(parent_dir, label)
        for label in os.listdir(path):
            artifact_path = os.path.join(path, label)
            artifact = load_artifact(artifact_path)
            subgroup.add_artifact(artifact)
        return subgroup

    def create_artifact(self, label: str, content: bytes, type: str, overwrite: bool = False) -> "ArtifactSubGroup":
        """
        Creates a new artifact and adds it to the subgroup.

        Parameters
        ----------
        self : ArtifactSubGroup
            The current object.
        label : str
            The label of the new artifact.
        content : Any
            The content of the new artifact.
        type : str
            The type of the new artifact.
        overwrite : bool, optional
            Whether to overwrite an existing artifact with the same label (default is False).

        Returns
        -------
        ArtifactSubGroup
            The current object.
        """

        if hasattr(self, label) and not overwrite:
            raise ExistingAttributeError(self, label)
        artifact = self._set_artifact_to_be_added(label=label, content=content, type=type)
        self._add_artifact(artifact)
        return self

    def add_artifact(self, artifact: Artifact, overwrite: bool = False) -> "ArtifactSubGroup":
        """
        Adds an existing artifact to the subgroup.

        Parameters
        ----------
        self : ArtifactSubGroup
            The current object.
        artifact : Artifact
            The artifact to be added.
        overwrite : bool, optional
            Whether to overwrite an existing artifact with the same label (default is False).

        Returns
        -------
        ArtifactSubGroup
            The current object.
        """
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

    def remove_artifact(self, label: str) -> "ArtifactSubGroup":
        """
        Remove a specific artifact from the list of artifacts and from the object attributes.
        Also, removes the artifact folder from the file system.

        Parameters:
        -----------
        label: str
            Label of the artifact to be removed.

        Returns:
        --------
        ArtifactSubGroup
            The same object of the class 'ArtifactSubGroup', but with the artifact removed.
        """
        self._remove_artifact_attribute(label)
        self._remove_artifact_from_list(label)
        self._remove_artifact_dir(label)
        return self

    def update_artifacts_paths(self) -> "ArtifactSubGroup":
        """
        Updates the paths of all artifacts in this ArtifactSubGroup.

        This method should be called whenever the parent directory or label of the ArtifactSubGroup changes.
        """
        new_parent_dir = os.path.join(self.parent_dir, self.label)
        for art in self.artifacts:
            art.set_path(new_parent_dir, art.label)
        return self

    def set_path(self, parent_dir: str, label: str) -> None:
        """
        Set the path of the subgroup by joining the parent directory and label.

        Parameters
        ----------
        parent_dir : str
            The parent directory of the subgroup.
        label : str
            The label of the subgroup.

        Returns
        -------
        None
        """
        self.path = os.path.join(parent_dir, label)

    def update(self):
        """
        Update the `ArtifactSubGroup` object after modifying its artifacts list.

        This method should be called every time the artifacts list is modified, in order to ensure that the object
        has consistent state. It removes any artifact attribute that is no longer present in the artifacts list, and
        sets the path of the artifacts to the current subgroup path.

        Returns
        -------
        None
        """
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

    def _remove_artifact_dir(self, label: str):
        directory = os.path.join(self.path, label)
        logger.warning(f"Removing folder {directory}")
        files.remove_directory(directory, recursive=True)


@dataclass
class ArtifactGroup:
    """
    A class that represents a group of artifacts.

    Attributes
    ----------
    label : str
        The name of the artifact group.
    parent_dir : str
        The path of the directory that contains the artifact group.
    path : Optional[str], default=None
        The path of the artifact group directory.
    subgroups : List[ArtifactSubGroup], default_factory=list
        A list containing the subgroups of the artifact group.

    Methods
    -------
    save() -> 'ArtifactGroup':
        Saves the artifacts of the artifact group to disk.
    load(label: str, parent_dir: str) -> 'ArtifactGroup':
        Loads an artifact group from disk.
    add_subgroup(subgroup: ArtifactSubGroup, overwrite: bool = False) -> 'ArtifactGroup':
        Adds a subgroup to the artifact group.
    create_subgroup() -> None:
        Creates a new subgroup.
    remove_subgroup(label: str) -> None:
        Removes a subgroup from the artifact group.
    set_path(parent_dir: str, label: str) -> None:
        Sets the path of the artifact group directory.
    update() -> None:
        Updates the artifact group after a change has been made.
    """

    label: str
    parent_dir: str
    path: Optional[str] = None
    subgroups: List[ArtifactSubGroup] = Field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Initializes the artifact group.

        Parameters
        ----------
        self : ArtifactGroup
            The artifact group to initialize.
        """
        self.set_path(self.parent_dir, self.label)
        self.update()

    class Config:
        arbitrary_types_allowed = True

    def save(self) -> "ArtifactGroup":
        """
        Saves the artifacts of the artifact group to disk.

        Returns
        -------
        ArtifactGroup
            The artifact group that was saved.
        """
        if not isinstance(self.subgroups, FieldInfo):
            for subgroup in self.subgroups:
                subgroup.save()

        return self

    @classmethod
    def load(cls, label: str, parent_dir: str) -> "ArtifactGroup":
        """
        Loads an artifact group from disk.

        Parameters
        ----------
        label : str
            The name of the artifact group.
        parent_dir : str
            The path of the directory that contains the artifact group.

        Returns
        -------
        ArtifactGroup
            The artifact group that was loaded.
        """
        group = ArtifactGroup(label=label, parent_dir=parent_dir)
        path = os.path.join(parent_dir, label)
        for label in os.listdir(path):
            subgroup_path = os.path.join(path, label)
            subgroup = cls._load_subgroup(subgroup_path)
            group.add_subgroup(subgroup)
        return group

    def add_subgroup(self, subgroup: ArtifactSubGroup, overwrite=False) -> "ArtifactGroup":
        """
        Add an ArtifactSubGroup instance to the ArtifactGroup's list of subgroups.

        Parameters
        ----------
        subgroup : ArtifactSubGroup
            The subgroup to add.
        overwrite : bool, optional
            Whether to overwrite an existing subgroup with the same label if one is found.
            If False and a subgroup with the same label exists, an ExistingAttributeError is raised.
            Default is False.

        Returns
        -------
        ArtifactGroup
            The ArtifactGroup instance.
        """
        pass
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

    def remove_subgroup(self, label: str) -> "ArtifactGroup":
        """
        Remove an ArtifactSubGroup instance from the ArtifactGroup's list of subgroups.

        Parameters
        ----------
        label : str
            The label of the subgroup to remove.

        Returns
        -------
        ArtifactGroup
            The ArtifactGroup instance.

        """
        self._remove_subgroup_attribute(label)
        self._remove_subgroup_from_list(label)
        return self

    def set_path(self, parent_dir: str, label: str) -> None:
        """
        Set the ArtifactGroup's path attribute to the given parent directory and label.

        Parameters
        ----------
        parent_dir : str
            The parent directory of the ArtifactGroup.
        label : str
            The label of the ArtifactGroup.

        Returns
        -------
        None

        """
        self.path = os.path.join(parent_dir, label)

    def update(self) -> None:
        """Updates the ArtifactGroup instance.

        This method removes any subgroup attributes that do not exist in the subgroups list
        and adds any new subgroups that exist in the subgroups list but do not have an attribute yet.

        Returns
        -------
        None
        """
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
    """
    A class for managing artifacts of a specific version.

    Parameters
    ----------
    parent_dir : str
        The path of the parent directory where the artifacts will be stored.

    Attributes
    ----------
    parent_dir : str
        The path of the parent directory where the artifacts will be stored.
    path : str
        The path of the directory where the artifacts of the current version are stored.
    data : ArtifactGroup
        The data artifacts of the current version.
    models : ArtifactGroup
        The models artifacts of the current version.
    _data_group_name : str
        The name of the data artifact group. Default is "data".
    _models_group_name : str
        The name of the models artifact group. Default is "models".
    _version_handler : VersionHandler
        An instance of VersionHandler class used for managing the versions of the artifacts.

    Examples
    --------
    >>> # Create Artifacts
    >>> ah = ArtifactHandler(parent_dir="/path/to/model/directory")
    >>> ah.data.raw.create_artifact(label="X_train", content=X_train, type="csv")
    >>> ah.data.raw.create_artifact(label="X_test", content=X_test, type="csv")
    >>> ah.data.raw.create_artifact(label="X_predict", content=X_predict, type="csv")
    >>> ah.data.raw.create_artifact(label="y_train", content=y_train, type="csv")
    >>> ah.data.raw.create_artifact(label="y_test", content=y_test, type="csv")
    >>> ah.data.transformed.create_artifact(label="X_train_transformed", content=X_train_transformed, type="parquet")
    >>> ah.data.transformed.create_artifact(label="X_test_transformed", content=X_test_transformed, type="parquet")
    >>> ah.models.transformers.create_artifact(label="scaler", content=scaler, type="binary")
    >>> ah.models.estimators.create_artifact(label="estimator", content=estimator, type="binary")
    ----
    >>> # Saving to local file
    >>> ah.commit()
    ----
    >>> # Update version
    >>> ah.increment_version_patch()
    >>> ah.commit()
    ----
    >>> # Importing
    >>> ah = ArtifactHandler("/path/to/model/directory").pull()
    ----
    >>> # Getting artifacts
    >>> X_train = ah.data.raw.X_train.get()
    >>> X_test = ah.data.raw.X_train.get()
    >>> transfomer = ah.models.transformers.scaler.get()
    >>> estimator = ah.models.estimators.estimator.get()
    """

    _data_group_name = "data"
    _models_group_name = "models"

    def __init__(self, parent_dir: str):
        """
        Initialize an ArtifactHandler instance.

        Parameters
        ----------
        parent_dir : str
            The path of the parent directory where the artifacts will be stored.
        """
        self.parent_dir = parent_dir
        self.path = None
        self._version_handler = VersionHandler(self.parent_dir)
        self._set_version()
        self._set_path()
        self.data: ArtifactGroup = self._set_data()
        self.models: ArtifactGroup = self._set_models()

    @property
    def version(self) -> str:
        """
        The current version of the artifacts.

        Returns
        -------
        str
            The current version of the artifacts.
        """
        return self._version_handler.latest_version

    @classmethod
    def load(cls, parent_dir: str) -> "ArtifactHandler":
        """
        Load an ArtifactHandler instance from the artifacts stored in the given directory.

        Parameters
        ----------
        parent_dir : str
            The path of the parent directory where the artifacts are stored.

        Returns
        -------
        ArtifactHandler
            An instance of ArtifactHandler class.
        """
        ah = cls(parent_dir=parent_dir)
        return cls._load_from_file(ah, parent_dir)

    def pull(self) -> "ArtifactHandler":
        """
        Load the latest version of the artifacts from the parent directory.

        Returns
        -------
        ArtifactHandler
            An instance of ArtifactHandler class.
        """
        return self._load_from_file(self, self.parent_dir)

    def increment_version_patch(self) -> "ArtifactHandler":
        """
        Increments the patch version of the artifact handler's version and saves the data and models artifact groups.

        Returns
        -------
        ArtifactHandler
            The updated artifact handler.

        """
        self.commit()
        old_dirname = self.version.dirname
        release = list(self.version.release)
        release[-1] = int(release[-1]) + 1
        new_version_string = ".".join([str(r) for r in release])
        self._version_handler.add_new_version(new_version_string)
        new_dirname = self.version.dirname
        copy_tree(self.path, self.path.replace(old_dirname, new_dirname))
        self._update_version_handler()
        return self

    def commit(self) -> "ArtifactHandler":
        """
        Saves the data and models artifact groups.

        Returns
        -------
        ArtifactHandler
            The updated artifact handler.

        """
        self.data.save()
        self.models.save()
        return self

    @staticmethod
    def _load_from_file(ah: "ArtifactHandler", parent_dir: str) -> "ArtifactHandler":
        path = os.path.join(parent_dir, f"version={ah.version}")
        for group in [ah._data_group_name, ah._models_group_name]:
            artifact_group = ArtifactGroup.load(label=group, parent_dir=path)
            setattr(ah, group, artifact_group)
        return ah

    def _update_version_handler(self):
        self._version_handler = VersionHandler(self.parent_dir)
        self._set_version()
        self._set_path()
        self.data: ArtifactGroup = self._set_data()
        self.models: ArtifactGroup = self._set_models()

    def _set_path(self):
        self.path = os.path.join(self.parent_dir, self.version.dirname)

    def _set_version(self):
        if self.version is None:
            self._version_handler.add_new_version("0.0.0")

    def _set_data(self):
        return ArtifactGroup(
            label=self._data_group_name,
            parent_dir=self.path,
            subgroups=[
                ArtifactSubGroup(label="raw", parent_dir=os.path.join(self.path, self._data_group_name)),
                ArtifactSubGroup(label="interim", parent_dir=os.path.join(self.path, self._data_group_name)),
                ArtifactSubGroup(label="transformed", parent_dir=os.path.join(self.path, self._data_group_name)),
                ArtifactSubGroup(label="predicted", parent_dir=os.path.join(self.path, self._data_group_name)),
            ],
        )

    def _set_models(self):
        return ArtifactGroup(
            label=self._models_group_name,
            parent_dir=self.path,
            subgroups=[
                ArtifactSubGroup(label="data", parent_dir=os.path.join(self.path, self._models_group_name)),
                ArtifactSubGroup(label="estimators", parent_dir=os.path.join(self.path, self._models_group_name)),
                ArtifactSubGroup(label="transformers", parent_dir=os.path.join(self.path, self._models_group_name)),
            ],
        )
