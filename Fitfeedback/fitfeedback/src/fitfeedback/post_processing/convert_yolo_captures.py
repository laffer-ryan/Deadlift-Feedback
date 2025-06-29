import numpy as np
import pandas as pd

def convert_yolo_captures_to_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert NA's and 0s in pipeline results to YOLO keypoints
    """
    for col in df.columns:
        if col.endswith('_pred_processed'):
            # Derive the corresponding YOLO column name
            yolo_col = col.replace('_pred_processed', '_pred_yolo')

            # Ensure the YOLO column exists
            if yolo_col in df.columns:
                # Replace NaN or 0 in the processed column with the YOLO value
                df[col] = np.where(df[col].isna() | (df[col] == 0.0), df[yolo_col], df[col])

    return df