import pandas as pd
import numpy as np

def get_keypoint_values(df: pd.DataFrame, side: str = 'left') -> tuple:
    if side == 'front':
        side = 'left' 
    wrist_y = df[f'{side}_wrist_y']
    ankle_y = df[f'{side}_ankle_y']
    knee_y = df[f'{side}_knee_y']
    # hip_y = df[f'{side}_hip_y']
    shoulder_y = df[f'{side}_shoulder_y']
    frame_count = df['frame_count']
    return wrist_y, ankle_y, knee_y, shoulder_y, frame_count


def get_start_velocity_idx(wrist_y: pd.Series, velocity_threshold: float = 0.0) -> pd.Series:
    """
    Calculate the minimum velocity of the wrist keypoint based on movement threshold.
    """
    wrist_vel = wrist_y.diff().fillna(0) 
    lift_off_idx = wrist_vel[wrist_vel < -velocity_threshold].index.min()
    if pd.isna(lift_off_idx):
        lift_off_idx = wrist_vel.idxmin()
    return lift_off_idx  




def get_downward_velocity_bounds(
    wrist_y: pd.Series,
    ext_idx: int,
    velocity_threshold: float = 1.5,
    stop_threshold: float = 0.1
) -> tuple[int, int]:
    """
    Finds the start and end indices of significant downward wrist motion after full extension.

    Args:
        df: Pandas DataFrame with pose data.
        wrist_y: Series of wrist y-positions.
        ext_idx: Index where full extension occurs.
        velocity_threshold: Start detecting downward motion when velocity > this.
        stop_threshold: Consider downward motion ended when velocity < this.

    Returns:
        start_index, end_index for downward motion.
    """
    wrist_vel = wrist_y.diff().fillna(0)
    # Ensure full Series is printed in terminal
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(f'Wrist Y: \n{wrist_y}\n')
        print(f'Wrist Velocity: \n{wrist_vel}\n')
    post_ext_vel = wrist_vel.loc[ext_idx + 1:]

    # 1. Find start of downward motion
    drop_start_idx = post_ext_vel[post_ext_vel > velocity_threshold].index.min()
    if pd.isna(drop_start_idx):
        drop_start_idx = post_ext_vel.idxmax()
    print(f'Drop Start Index: {drop_start_idx}')
    # 2. Find end of downward motion — after start, when velocity < stop_threshold

    drop_end_idx = None
    if not pd.isna(drop_start_idx):
        remaining = wrist_vel.loc[drop_start_idx + 1:].abs()
        remaining_below = remaining < stop_threshold
        print(f'Remaining below stop threshold: \n{remaining_below}\n')
        indices = remaining_below.index.to_list()
        for i in range(len(indices) - 1):
            if remaining_below.loc[indices[i]] and remaining_below.loc[indices[i + 1]]:
                drop_end_idx = indices[i]
                break

        # If no pair of consecutive low-velocity points found
        if drop_end_idx is None:
            drop_end_idx = remaining.index[-2]


    return drop_start_idx, drop_end_idx





# For front view only
def get_distance_progress_checkpoints(
    df: pd.DataFrame,
    start_idx: int,
    end_idx: int,
    progress_factors=(0.50, 0.60, 0.70, 0.80, 0.90)
) -> list:
    """
    Calculates indices where the wrist is at specific proportions along the hip vector (ankle to hip).
    Only considers frames between liftoff and extension.

    Args:
        df: Pandas DataFrame with keypoints.
        start_idx: Index for lift-off (start of deadlift).
        end_idx: Index for full extension (end of deadlift).
        progress_factors: Tuple of fractions to define checkpoints.

    Returns:
        List of indices where wrist is nearest to each target point along the hip.
    """

    # Restrict frame range to between liftoff and extension
    df_segment = df.loc[start_idx:end_idx].copy()

    # Average left and right coordinates
    hip_x = (df_segment['left_hip_x'] + df_segment['right_hip_x']) / 2
    hip_y = (df_segment['left_hip_y'] + df_segment['right_hip_y']) / 2
    ankle_x = (df_segment['left_ankle_x'] + df_segment['right_ankle_x']) / 2
    ankle_y = (df_segment['left_ankle_y'] + df_segment['right_ankle_y']) / 2
    wrist_x = (df_segment['left_wrist_x'] + df_segment['right_wrist_x']) / 2
    wrist_y = (df_segment['left_wrist_y'] + df_segment['right_wrist_y']) / 2

    # Shin unit vector
    dx = hip_x - ankle_x
    dy = hip_y - ankle_y
    magnitude = np.sqrt(dx**2 + dy**2).replace(0, 1e-6)
    ux = dx / magnitude
    uy = dy / magnitude

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(f'Wrist Y: \n{wrist_y}\n')
    
    # Get target points and find closest indices
    indices = []
    for factor in progress_factors:
        target_x = ankle_x + factor * ux * magnitude
        target_y = ankle_y + factor * uy * magnitude

        distances = (wrist_x - target_x)**2 + \
                    (wrist_y - target_y)**2

        idx_local = distances.idxmin()
        indices.append(idx_local)

    return indices





# Side view checkpoint
def get_torso_slope_checkpoints(df: pd.DataFrame, side: str = 'left', angle_thresholds=(40, 50, 60, 70, 80), start_idx=1, end_idx = 1) -> tuple:
    """
    Calculates the angle (in degrees) between the line connecting shoulder and hip.
    Returns the indices where the torso angle is closest to the given angle thresholds.

    Args:
        df: Pandas DataFrame with keypoints.
        side: 'left' or 'right'
        angle_thresholds: Tuple of 3 target torso angles in degrees (from horizontal)

    Returns:
        indices of tuple for each angle threshold
    """
    df_copy = df.copy()
    shoulder_x = df_copy[f'{side}_shoulder_x']
    shoulder_y = df_copy[f'{side}_shoulder_y']
    hip_x = df_copy[f'{side}_hip_x']
    hip_y = df_copy[f'{side}_hip_y']

    # Calculate rise/run
    if side == 'left':
        dx = shoulder_x - hip_x
        dy = shoulder_y - hip_y
    else:  # Right view — reverse dx to make slope direction consistent
        dx = hip_x - shoulder_x
        dy = hip_y - shoulder_y

    # Avoid divide-by-zero
    dx = dx.replace(0, 1e-6)

    # Convert to angle in degrees
    angles_rad = np.arctan2(dx, dy)
    angles_deg = np.degrees(angles_rad).abs()


    # Optional: add angle column to df_copy for inspection
    df_copy['torso_angle_deg'] = angles_deg

    # Ensure angle is calculated for point after liftoff
    df_copy_post_liftoff = df_copy.loc[start_idx:end_idx + 1].copy()
    angle_series = df_copy_post_liftoff['torso_angle_deg']

    # Find the index closest to each target angle
    indices = []
    for target_angle in angle_thresholds:
        idx = (angle_series - target_angle).abs().idxmin()
        indices.append(idx)
    print('\n\nAngles')
    print(df_copy_post_liftoff[['frame_count', 'torso_angle_deg']])
    return indices[0], indices[1], indices[2], indices[3], indices[4]
