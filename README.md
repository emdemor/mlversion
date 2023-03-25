# MLVersion

MLVersion is a Python package that simplifies version management for machine learning models. With MLVersion, you can easily keep track of your model's version history, prevent repeated versions, and create new version folders in your specified directory. MLVersion is designed to streamline your workflow and keep your versioning organized, allowing you to focus on what you do best: developing cutting-edge machine learning models.


## Installation

To install MLVersion, simply run:

```sh
pip install mlversion
```

## Usage

To use MLVersion, first import the `VersionHandler` class:

```python
from MLVersion.version_handler import VersionHandler
```

Then, instantiate the `VersionHandler` with the path to the directory where the model versions will be stored:

```python
version_handler = VersionHandler("/path/to/versions/directory")
```

Once the `VersionHandler` is instantiated, you can add a new version to the directory:

```python
version_handler.add_new_version("1.0.0")
```

If the version string is not valid according to the package's format, it will raise an `InvalidVersion` exception. If the version already exists in the directory, it will raise an `ExistingVersionError` exception.

You can also get the history of versions created by accessing the `history` attribute of the `VersionHandler`:

```python
versions = version_handler.history
```

This will return a list of `Version` objects, which can be used to compare versions and get version numbers in various formats.

Finally, you can get the latest version in the directory by accessing the `latest_version` attribute of the `VersionHandler`:

```python
latest_version = version_handler.latest_version
```

This will return the `Version` object corresponding to the latest version created in the directory.

## Contributing

We welcome contributions to MLVersion! To contribute, please fork the repository, create a branch for your changes, and submit a pull request.

Before submitting a pull request, please make sure to run the test suite:

```sh
python -m unittest discover
```

Please also make sure to follow the [code of conduct](CODE_OF_CONDUCT.md) and the [contribution guidelines](CONTRIBUTING.md).

## License

MLVersion is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
