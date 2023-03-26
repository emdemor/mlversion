import os
from pathlib import Path
from typing import Any,  Union

import joblib
import pandas as pd
from tabulate import tabulate


def _get_dataframe_representation(df):
    df_break = df.head(5)
    if len(df) > 5:
        index = list(df_break.index) + ["..."]
        df_break = df_break.append(pd.Series(len(df.columns) * ['...'], index=df.columns), ignore_index=True)
        df_break.index = index

    return tabulate(df_break, headers='keys', tablefmt='psql')


def save_bin(obj: Any, path: str) -> None:
    create_folder_chain(path)
    joblib.dump(obj, path)


def load_bin(path: str) -> Any:
    return joblib.load(path)


def create_folder_chain(path: Union[str, Path]) -> None:
    path_obj = Path(path)
    if path_obj.is_dir():
        os.makedirs(path_obj, exist_ok=True)
    else:
        parent_dir = path_obj.parent
        os.makedirs(parent_dir, exist_ok=True)
