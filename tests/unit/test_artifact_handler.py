import numpy as np
import pandas as pd
from mlversion._artifact_handler import ArtifactSubGroup
from mlversion._artifacts import CSVArtifact, BinaryArtifact


def test_csv_artifact(csv_artifact):
    csv_artifact.save()
    artifact_imported = CSVArtifact.load(label="train", parent_dir="workdir/test/data/")

    df = csv_artifact.get()
    df_imported = artifact_imported.get()

    assert df.equals(df_imported)


def test_binary_artifact(bin_artifact):
    expected_value = bin_artifact.get().predict([[2]])[0]
    bin_artifact.save()

    imported_artifact = BinaryArtifact.load(
        label="linear_regression", parent_dir="workdir/test/models/"
    )
    prediction = imported_artifact.get().predict([[2]])[0]

    assert np.isclose(expected_value, prediction)


def test_artifact_subgroup(artifact_subgroup):

    artifact_subgroup.save()

    artifact_subgroup_imported = ArtifactSubGroup.load(label="artifact_subgroup", parent_dir="workdir/test/")

    assert hasattr(artifact_subgroup_imported, "train")
    assert hasattr(artifact_subgroup_imported, "linear_regression")


def test_create_artifact_in_subgroup(artifact_subgroup):

    df = df = pd.DataFrame([[0, 10], [1, 20]], columns=["x", "y"])

    artifact_subgroup = artifact_subgroup.create_artifact(
        label="new_artifact",
        content = df,
        type = "csv_table",
    ).save()

    artifact_subgroup_imported = ArtifactSubGroup.load(label="artifact_subgroup", parent_dir="workdir/test/")

    assert hasattr(artifact_subgroup_imported, "new_artifact")
