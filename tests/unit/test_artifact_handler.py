from loguru import logger
import pandas as pd
from mlversion._artifact_handler import CSVArtifact, ArtifactGroup, ArtifactSubGroup

def test_artifact():
    df = pd.DataFrame([[0,10],[1,12]], columns=["id", "value"])
    artifact = CSVArtifact(label="train", content=df, parent_dir="workdir/data/")

    logger.warning(artifact.path)
    
    #artifact.save()
    #df = pd.read_csv("workdir/data/train.csv")


# def test_artifact_handler(artifact_handler: ArtifactHandler):
#     ...


# def test_artifact_handler_instance(models_path: str):

#     subgroup_raw = ArtifactSubGroup(label="raw")
#     subgroup_interim = ArtifactSubGroup(label="interim")
#     subgroup_transformed = ArtifactSubGroup(label="transformed")
#     subgroup_predicted = ArtifactSubGroup(label="predicted")

#     group = ArtifactGroup(
#         label="data",
#         artifacts_subgroups=[
#             subgroup_raw,
#             subgroup_interim,
#             subgroup_transformed,
#             subgroup_predicted,
#         ]
#     )
    # artifact_handler = ArtifactHandler(models_path)

    # logger.info(artifact_handler.data)
    # logger.info(artifact_handler.data.raw)