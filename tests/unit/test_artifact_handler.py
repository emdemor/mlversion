from loguru import logger
import numpy as np
import pandas as pd
from mlversion._artifact_handler import ArtifactSubGroup, ArtifactGroup
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

    imported_artifact = BinaryArtifact.load(label="linear_regression", parent_dir="workdir/test/models/")
    prediction = imported_artifact.get().predict([[2]])[0]

    assert np.isclose(expected_value, prediction)


def test_artifact_subgroup(artifact_subgroup):

    artifact_subgroup.save()

    artifact_subgroup_imported = ArtifactSubGroup.load(label="poc", parent_dir="workdir/test/")

    assert hasattr(artifact_subgroup_imported, "train")
    assert hasattr(artifact_subgroup_imported, "linear_regression")


def test_create_artifact_in_subgroup(artifact_subgroup):

    df = df = pd.DataFrame([[0, 10], [1, 20]], columns=["x", "y"])

    artifact_subgroup = artifact_subgroup.create_artifact(
        label="new_artifact",
        content=df,
        type="csv_table",
    ).save()

    artifact_subgroup_imported = ArtifactSubGroup.load(label="poc", parent_dir="workdir/test/")

    assert hasattr(artifact_subgroup_imported, "new_artifact")


def test_remove_artifact_in_subgroup(artifact_subgroup):

    has_train_start = hasattr(artifact_subgroup, "train")

    assert has_train_start
    assert any([a.label == "train" for a in artifact_subgroup.artifacts])

    artifact_subgroup.remove_artifact(label="train")

    has_train_end = hasattr(artifact_subgroup, "train")

    assert not has_train_end
    assert all([a.label != "train" for a in artifact_subgroup.artifacts])


def test_artifact_group(artifact_group, csv_artifact, bin_artifact):

    parent_dir = "workdir/test/"

    mvp = ArtifactSubGroup(label="mvp", parent_dir=parent_dir).add_artifact(csv_artifact).add_artifact(bin_artifact)

    group = (
        artifact_group
        .add_subgroup(mvp)
        .save()
    )

    group_imported = ArtifactGroup.load(label="clustering", parent_dir=parent_dir)

    subgroups = sorted([s.label for s in group.subgroups])
    imported_subgroups = sorted([s.label for s in group_imported.subgroups])

    assert all([(a, b) for a, b in zip(subgroups, imported_subgroups)])


def test_remove_subgroup_from_artifact_group(artifact_group, csv_artifact, bin_artifact):
    parent_dir = "workdir/test/"
    mvp = ArtifactSubGroup(label="mvp", parent_dir=parent_dir).add_artifact(csv_artifact).add_artifact(bin_artifact)
    group = (
        artifact_group
        .add_subgroup(mvp)
        .save()
    )
    group_imported = ArtifactGroup.load(label="clustering", parent_dir=parent_dir)

    group_imported = group_imported.remove_subgroup("mvp")

    assert hasattr(group, "mvp")
    assert not hasattr(group_imported, "mvp")
