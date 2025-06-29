import numpy as np
import pandas as pd

def get_point(row, name):
    return row[f"{name}_x"], row[f"{name}_y"]

def calculate_angle(a, b, c):
    """Calculate the angle at point b (in degrees) given three (x, y) points a, b, c."""
    
    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b)
    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)
    
    if norm_ba == 0 or norm_bc == 0:
        return np.nan  # Undefined angle due to degenerate vector
    
    cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

# Angle functions for each joint

def left_elbow_angle(row):
    return calculate_angle(get_point(row, 'left_wrist'), get_point(row, 'left_elbow'), get_point(row, 'left_shoulder'))

def right_elbow_angle(row):
    return calculate_angle(get_point(row, 'right_wrist'), get_point(row, 'right_elbow'), get_point(row, 'right_shoulder'))

def left_knee_angle(row):
    return calculate_angle(get_point(row, 'left_ankle'), get_point(row, 'left_knee'), get_point(row, 'left_hip'))

def right_knee_angle(row):
    return calculate_angle(get_point(row, 'right_ankle'), get_point(row, 'right_knee'), get_point(row, 'right_hip'))

def left_hip_angle(row):
    return calculate_angle(get_point(row, 'left_knee'), get_point(row, 'left_hip'), get_point(row, 'left_shoulder'))

def right_hip_angle(row):
    return calculate_angle(get_point(row, 'right_knee'), get_point(row, 'right_hip'), get_point(row, 'right_shoulder'))

def lower_left_wrist_angle(row):
    return calculate_angle(get_point(row, 'left_ankle'), get_point(row, 'left_wrist'), get_point(row, 'left_hip'))

def lower_right_wrist_angle(row):
    return calculate_angle(get_point(row, 'right_ankle'), get_point(row, 'right_wrist'), get_point(row, 'right_hip'))

def upper_left_wrist_angle(row):
    return calculate_angle(get_point(row, 'left_shoulder'), get_point(row, 'left_wrist'), get_point(row, 'left_hip'))

def upper_right_wrist_angle(row):
    return calculate_angle(get_point(row, 'right_shoulder'), get_point(row, 'right_wrist'), get_point(row, 'right_hip'))

def neck_angle_left(row):
    return calculate_angle(get_point(row, 'nose'), get_point(row, 'left_shoulder'), get_point(row, 'left_hip'))

def neck_angle_right(row):
    return calculate_angle(get_point(row, 'nose'), get_point(row, 'right_shoulder'), get_point(row, 'right_hip'))

def posterior_chain_left(row):
    return calculate_angle(get_point(row, 'left_shoulder'), get_point(row, 'left_hip'), get_point(row, 'left_ankle'))

def posterior_chain_right(row):
    return calculate_angle(get_point(row, 'right_shoulder'), get_point(row, 'right_hip'), get_point(row, 'right_ankle'))


def left_to_right_shoulder_slope(row):
    """
    Returns the slope of the line connecting the left and right shoulders.
    0 degrees means perfectly horizontal (left to right).
    Positive means right shoulder is higher than left.
    """
    left_shoulder = get_point(row, 'left_shoulder')
    right_shoulder = get_point(row, 'right_shoulder')
    dx = right_shoulder[0] - left_shoulder[0]
    dy = right_shoulder[1] - left_shoulder[1]
    return dy / dx if dx != 0 else np.nan

def left_right_wrist_slope(row):
    """
    Returns the slope of the line connecting the left and right wrists.
    Positive means right wrist is higher than left.
    """
    left_wrist = get_point(row, 'left_wrist')
    right_wrist = get_point(row, 'right_wrist')
    dx = right_wrist[0] - left_wrist[0]
    dy = right_wrist[1] - left_wrist[1]
    return dy / dx if dx != 0 else np.nan


def head_tilt_slope(row):
    """Slope between left_eye and right_eye."""
    left_eye = get_point(row, 'left_eye')
    right_eye = get_point(row, 'right_eye')
    dx = right_eye[0] - left_eye[0]
    dy = right_eye[1] - left_eye[1]
    return dy / dx if dx != 0 else np.nan

def calculate_hip_angle(df: pd.DataFrame, side: str = 'left') -> pd.Series:
    """Calculate the hip angle for all frames for a given side ('left' or 'right')."""
    if side == 'left':
        return df.apply(left_hip_angle, axis=1)
    else:
        return df.apply(right_hip_angle, axis=1)

