import pandas as pd



def apply_confidence_threshold(df: pd.DataFrame, threshold: float = 0.80) -> pd.DataFrame:
    """
    If confidence for bodypart is below the threshold, set the _x and _y columns to 0.0.
    Assumes columns are named as 'bodypart_x', 'bodypart_y', and 'bodypart_confidence'.
    """
    for col in df.columns:
        if col.endswith('_confidence'):
            bodypart = col.replace('_confidence', '')
            x_col = f'{bodypart}_x'
            y_col = f'{bodypart}_y'
            if x_col in df.columns and y_col in df.columns:
                mask = df[col] < threshold
                df.loc[mask, x_col] = 0.0
                df.loc[mask, y_col] = 0.0
    return df