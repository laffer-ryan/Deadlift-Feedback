import pandas as pd


def split_keypoint_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Splits all columns ending with '_keypoint' into separate _x and _y columns.
    Assumes each value is a list or tuple of two floats.
    """
    new_df = df.copy()
    keypoint_cols = [col for col in new_df.columns if col.endswith('_keypoint')]
    
    for col in keypoint_cols:
        base = col.replace('_keypoint', '').replace(' ', '_')
        new_df[f'{base}_x'] = new_df[col].apply(lambda v: v[0] if isinstance(tuple(v), tuple) and len(v) == 2 else None)
        new_df[f'{base}_y'] = new_df[col].apply(lambda v: v[1] if isinstance(tuple(v), tuple) and len(v) == 2 else None)
        new_df = new_df.drop(columns=[col])
    return new_df