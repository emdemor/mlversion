from loguru import logger
import pandas as pd
from tabulate import tabulate

def _get_dataframe_representation(df):
    df_break = df.head(5)
    if len(df) > 5:
        index = list(df_break.index) + ["..."]
        df_break = df_break.append(pd.Series(len(df.columns) * ['...'], index=df.columns), ignore_index=True)
        df_break.index = index

    return tabulate(df_break, headers='keys', tablefmt='psql')
