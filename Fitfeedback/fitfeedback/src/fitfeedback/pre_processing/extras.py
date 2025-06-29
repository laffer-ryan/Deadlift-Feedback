# This file includes additional functions for pre-processing and saving checkpoint frames.

import pandas as pd

def adjust_ankle_keypoints(df: pd.DataFrame, side: str = 'front') -> pd.DataFrame:
    """
    Adjusts ankle keypoints when values are NA because ankle keypoints don't move.
    For each ankle, fill NA with mean, then replace values < 1 with the median of that column (after filtering out values < 1).
    Args:
        df: DataFrame with keypoints
        side: 'left' or 'right' or 'front' to specify which ankle(s) to adjust
    Returns:
        pd.DataFrame: DataFrame with adjusted ankle keypoints
    """
    df = df.copy()
    # Helper to fix a single column
    width = df['orig_width'].iloc[0]
    height = df['orig_height'].iloc[0]

    def fix_col(col):
        # Fill NA with mean
        df[col] = df[col].fillna(df[col].mean())
        # Compute median of values >= 1
        valid = df[col][df[col] >= 1]
        median_val = valid.median() if not valid.empty else 1.0
        # Replace values < 1 with the median
        df[col] = df[col].apply(lambda x: median_val if x < 1 or x >= width or x >= height else x)

    if side in ['front', 'right']:
        fix_col('right_ankle_x')
        fix_col('right_ankle_y')
    if side in ['front', 'left']:
        fix_col('left_ankle_x')
        fix_col('left_ankle_y')
    return df


def fill_missing_keypoints(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fills missing keypoints with the mean of the column.
    """
    df = df.copy()
    df = df.fillna(0.0)
    return df


