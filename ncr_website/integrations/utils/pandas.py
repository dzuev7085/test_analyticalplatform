"""Helper functions for pandas."""
import pandas as pd


def print_df(df):
    """Print a data frame. Used for debuggning."""

    with pd.option_context('display.max_rows', 10, 'display.max_columns', 10):
        print(df)
