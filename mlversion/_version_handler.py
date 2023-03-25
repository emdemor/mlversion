import os
import re
from typing import List, Optional, Union

from loguru import logger
from basix import files
from packaging.version import Version, InvalidVersion


class VersionHandler:
    """
    A class to handle versions in a directory.

    Attributes:
    -----------
    path : str
        The directory path where the versions are stored.
        A list of Version objects with all the valid versions stored in the directory.
    latest_version : Union[None, Version]
        The latest version in the directory.

    Methods:
    --------
    add_new_version(version_string: str) -> None:
        Add a new version to the directory.
    """
    _version_pattern = r"(\d+\.\d+\.\d+(dev|rc)?\d*)(\w*)$"
    _version_pattern_regex = re.compile(_version_pattern)
    _version_dir_pattern_regex = re.compile(r"version=" + _version_pattern)

    def __init__(self, path: str) -> None:
        """
        Initialize a VersionHandler object.

        Parameters:
        -----------
        path : str
            The directory path where the versions are stored.
        """
        self.path = path

        self.versions: Union[None, List[str]] = None
        self.latest_version: Union[None, str] = None
        self._update()

    def add_new_version(self, version_string: str) -> None:
        """
        Add a new version to the directory.

        Parameters:
        -----------
        version_string : str
            The version string to add to the directory.

        Raises:
        -------
        InvalidVersion
            If the version string is not a valid version format.
        ExistingVersionError
            If the version already exists in the directory.
        """

        match = self._version_pattern_regex.search(version_string)

        if not match:
            raise InvalidVersion(f"'{version_string}' is not a valid version format.")

        self._create_version_directory(version_string)

        self._update()

    def _create_version_directory(self, version_string: str) -> None:
        """
        Create a directory with the name of the version in the directory.

        Parameters:
        -----------
        version_string : str
            The version string to add to the directory.

        Raises:
        -------
        ExistingVersionError
            If the version already exists in the directory.
        """

        if version_string in [version.base_version for version in self.history]:
            raise ExistingVersionError(
                f"Unable to add version {version_string} because it "
                "already exists in the folder {self.path}."
            )

        files.make_directory(os.path.join(self.path, f"version={version_string}"))

    def _get_versions(self) -> None:
        """
        Find existing versions in the specified folder and store them in `self.history`.
        The latest existing version is also stored in `self.latest_version`.
        """

        self.history = []

        latest_version = Version("0.0.0")

        for subdir in os.listdir(self.path):
            match = self._version_dir_pattern_regex.search(subdir)
            if match:
                version_str = match.group(1)
                try:
                    version = Version(version_str)
                    self.history.append(version)
                    if self._check_if_new_version_is_greater(
                        self.latest_version, version
                    ):
                        self.latest_version = version
                except InvalidVersion as exception:
                    pass

    def _update(self) -> None:
        """
        Update the version history and the latest existing version.
        """
        self._get_versions()

    @staticmethod
    def _check_if_new_version_is_greater(
        old_version: Optional[Version], new_version: Optional[Version]
    ) -> bool:
        """
        Check if the new version is greater than the old version.

        Parameters
        ----------
        old_version : Version or None
            The old version.
        new_version : Version or None
            The new version.

        Returns
        -------
        bool
            True if the new version is greater, False otherwise.

        Raises
        ------
        TypeError
            If both versions are None.
        """
        if (old_version is None) and (new_version is None):
            raise TypeError(
                f"It is not possible to compare versions since both are None."
            )

        if (old_version is None) and (new_version is not None):
            return True

        if (old_version is not None) and (new_version is None):
            return False

        if new_version > old_version:
            return True


class ExistingVersionError(Exception):
    pass
