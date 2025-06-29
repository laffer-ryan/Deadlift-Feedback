import pandas as pd
from collections import Counter

def determine_view(df: pd.DataFrame, missing_ratio_threshold: float = 0.1) -> str:
    """
    Determines if the video is 'front', 'side', or 'undetermined' based on the presence of keypoints.
    Args:
        df: DataFrame after running find_checkpoints (must have *_shoulder_x/y and *_hip_x/y columns)
        missing_ratio_threshold: Ratio of missing keypoints to consider a side view
    Returns:
        str: 'side', 'front', or 'undetermined'
    """
    left_keys = [col for col in df.columns if col.startswith('left_') and (col.endswith('_x') or col.endswith('_y'))]
    right_keys = [col for col in df.columns if col.startswith('right_') and (col.endswith('_x') or col.endswith('_y'))]
    n_frames = len(df)
    left_valid = (df[left_keys] > 0).all(axis=1).sum()
    right_valid = (df[right_keys] > 0).all(axis=1).sum()
    left_ratio = left_valid / n_frames
    right_ratio = right_valid / n_frames
    # If one side is mostly missing, it's a side view
    if left_ratio < (missing_ratio_threshold) and right_ratio >= missing_ratio_threshold:
        return 'right'
    if right_ratio < (missing_ratio_threshold) and left_ratio >= missing_ratio_threshold:
        return 'left'
    # If both sides are present in most frames, it's a front view
    if left_ratio >= missing_ratio_threshold and right_ratio >= missing_ratio_threshold:
        return 'front'
    # Otherwise, undetermined
    return 'undetermined'

# def determine_side_direction(df: pd.DataFrame, delta: float = 5.0) -> str:
#     """
#     Determines if the side view is 'left' or 'right'
#     Args:
#         df: DataFrame with 'mid_shoulder_x' and 'mid_hip_x' columns (as computed in determine_view)
#         delta: Small threshold to avoid ambiguity (in pixels)
#     Returns:
#         str: 'right', 'left', or 'undetermined'
#     """
#     # Use the median to be robust to outliers
#     shoulder_x = df['mid_shoulder_x'].median()
#     print(f"Shoulder X median: {shoulder_x}")  # Debugging output
#     hip_x = df['mid_hip_x'].median()
#     print(f"Hip X median: {hip_x}")  # Debugging output
#     if shoulder_x > hip_x + delta:
#         return 'right'
#     elif shoulder_x < hip_x - delta:
#         return 'left'
#     else:
#         return 'undetermined'

# def determine_camera_view(df: pd.DataFrame, slope_threshold: float = 3.73, delta: float = 10.0) -> str:
#     """
#     Determines the camera angle on the person
#     Args:
#         df: DataFrame after running find_checkpoints
#         slope_threshold: Threshold for classifying sagittal vs frontal view
#         delta: Small threshold for side direction to remove slight side to side movement in frontal view
#     Returns:
#         str: 'front', 'left', 'right', or 'undetermined'
#     """
#     majority_label = determine_view(df, slope_threshold)
#     if majority_label == 'front':
#         return 'front'
#     else:
#         return determine_side_direction(df, delta)


