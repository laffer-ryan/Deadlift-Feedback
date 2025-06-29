import numpy as np
import pandas as pd
import fitfeedback.metrics.angle_utility as angle_utility
import fitfeedback.metrics.distance_utility as distance_utility

def calculate_angles_and_distances(df: pd.DataFrame, side: str = 'left') -> pd.DataFrame:
    """
    Calculates angles between keypoints for the given side.
    """
    # Always calculate these for both sides if front, else just for the given side
    if side == 'left':
        df['bar_distance_from_body'] = df.apply(lambda row: distance_utility.bar_distance_from_body(row, 'left'), axis=1)
        df['left_elbow_angle'] = df.apply(angle_utility.left_elbow_angle, axis=1)
        df['lower_left_wrist_angle'] = df.apply(angle_utility.lower_left_wrist_angle, axis=1)
        df['upper_left_wrist_angle'] = df.apply(angle_utility.upper_left_wrist_angle, axis=1)
        df['neck_angle_left'] = df.apply(angle_utility.neck_angle_left, axis=1)
        df['posterior_chain_left'] = df.apply(angle_utility.posterior_chain_left, axis=1)

    if side == 'right':
        print("Calculating right side angles")
        df['bar_distance_from_body'] = df.apply(lambda row: distance_utility.bar_distance_from_body(row, 'right'), axis=1)
        df['right_elbow_angle'] = df.apply(angle_utility.right_elbow_angle, axis=1)
        df['lower_right_wrist_angle'] = df.apply(angle_utility.lower_right_wrist_angle, axis=1)
        df['upper_right_wrist_angle'] = df.apply(angle_utility.upper_right_wrist_angle, axis=1)
        df['neck_angle_right'] = df.apply(angle_utility.neck_angle_right, axis=1)
        df['posterior_chain_right'] = df.apply(angle_utility.posterior_chain_right, axis=1)

    if side == 'front':
        df['left_to_right_shoulder_slope'] = df.apply(angle_utility.left_to_right_shoulder_slope, axis=1)
        df['left_right_wrist_slope'] = df.apply(angle_utility.left_right_wrist_slope, axis=1)
        df['head_tilt_slope'] = df.apply(angle_utility.head_tilt_slope, axis=1)
        df['normalised_wrist_difference'] = df.apply(distance_utility.wrist_difference, axis=1)
        df['normalised_ankle_difference'] = df.apply(distance_utility.ankle_difference, axis=1)
        df['normalised_shoulder_distance'] = df.apply(distance_utility.shoulder_distance, axis=1)
        df['normalised_knee_distance'] = df.apply(distance_utility.knee_distance, axis=1)
        df['right_knee_lateral_distance_from_center'] = df.apply(distance_utility.right_knee_lateral_distance, axis=1)
        df['left_knee_lateral_distance_from_center'] = df.apply(distance_utility.left_knee_lateral_distance, axis=1)
        df['right_ankle_lateral_distance_from_center'] = df.apply(distance_utility.right_ankle_lateral_distance, axis=1)
        df['left_ankle_lateral_distance_from_center'] = df.apply(distance_utility.left_ankle_lateral_distance, axis=1)
        df['right_wrist_lateral_distance_from_center'] = df.apply(distance_utility.right_wrist_lateral_distance, axis=1)
        df['left_wrist_lateral_distance_from_center'] = df.apply(distance_utility.left_wrist_lateral_distance, axis=1)

    if side == 'left' or side == 'front':
        df['left_knee_angle'] = df.apply(angle_utility.left_knee_angle, axis=1)
        df['left_hip_angle'] = df.apply(angle_utility.left_hip_angle, axis=1)

    if side == 'right' or side == 'front':
        df['right_knee_angle'] = df.apply(angle_utility.right_knee_angle, axis=1)
        df['right_hip_angle'] = df.apply(angle_utility.right_hip_angle, axis=1)

    # Remove non relevant angles and distances
    df = remove_angles(df, side)
    print(df.columns)
    return df


def remove_angles(df: pd.DataFrame, side: str = 'left') -> pd.DataFrame:
    """
    Calculate angles for a specific side.
    Args:
        df: DataFrame with keypoints.
        side: 'left', 'right', or 'front'.
    Returns:
        DataFrame with angle columns for the specified side.
    """
    if side == 'left':
        columns = [col for col in df.columns if col.startswith('right')]
    elif side == 'right':
        columns = [col for col in df.columns if col.startswith('left')]
    else:
        columns = []
    return df.drop(columns=columns)

def bar_distance_from_body(df: pd.DataFrame, side: str) -> pd.Series:
    """
    Calculates the perpendicular distance from the left_wrist keypoint to the line
    defined by the left_ankle and left_knee keypoints for each row in the DataFrame.

    Returns a pandas Series with the distances.
    """
    # Extract coordinates
    x0 = df[f'{side}_wrist_x']
    y0 = df[f'{side}_wrist_y']
    x1 = df[f'{side}_ankle_x']
    y1 = df[f'{side}_ankle_y']
    x2 = df[f'{side}_knee_x']
    y2 = df[f'{side}_knee_y']

    # Line: (x1, y1) to (x2, y2)
    # Point: (x0, y0)
    # Distance formula:
    # |(y2 - y1)x0 - (x2 - x1)y0 + x2*y1 - y2*x1| / sqrt((y2 - y1)^2 + (x2 - x1)^2)
    numerator = np.abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    denominator = np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
    distance = numerator / (denominator + 1e-8)  # add epsilon to avoid division by zero

    return distance
