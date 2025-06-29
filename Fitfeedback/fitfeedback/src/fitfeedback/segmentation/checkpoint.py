import pandas as pd
from pprint import pprint
from fitfeedback.metrics.angle_utility import calculate_hip_angle
from fitfeedback.pre_processing.extras import fill_missing_keypoints, adjust_ankle_keypoints
from fitfeedback.segmentation.checkpoint_utils import get_downward_velocity_bounds, get_keypoint_values, get_torso_slope_checkpoints, get_start_velocity_idx, get_distance_progress_checkpoints



def get_checkpoints(df: pd.DataFrame, side: str = 'left') -> pd.DataFrame:
    """Calls the appropriate fucntion based an the camera angle"""

    df = adjust_ankle_keypoints(df, side=side)  
    df = fill_missing_keypoints(df)  

    if side == 'front':
        return find_checkpoints_front_view(df, side=side)
    elif side in ['left', 'right']:
        return find_checkpoints_side_view(df, side=side)
    else:
        raise ValueError(f"Invalid side: {side}. Must be 'left', 'right', or 'front'.")

def find_checkpoints_front_view(df: pd.DataFrame, side: str = 'left') -> pd.DataFrame:
    """
    Segments the deadlift into biomechanical checkpoints as defined in the provided table.
    Returns a DataFrame with one row per checkpoint and relevant keypoints with a label for that checkpoint.
    Args:
        df: DataFrame provided after Butterworth filtering.
        side: 'left' or 'right'.
    Returns:
        Dataframe
    """
    
    # keypoint values
    wrist_y, _, _, _, _ = get_keypoint_values(df, side=side)

    # 1. liftoff: first significant upward movement of wrist
    lift_off_idx = get_start_velocity_idx(wrist_y, velocity_threshold=0.5)

    # 2. Full Extension: hip angle > 170°
    hip_angles = calculate_hip_angle(df, side=side)
    idx_ext = hip_angles[hip_angles > 180].index.min()
    if pd.isna(idx_ext):
        idx_ext = hip_angles.idxmax()
    
    # 3. Downward motion after full extension
    drop_start_idx, drop_end_idx = get_downward_velocity_bounds(wrist_y, ext_idx=idx_ext, velocity_threshold=.5, stop_threshold=.1)
    print(f'\n\nDrop start index: {drop_start_idx}, Drop end index: {drop_end_idx}')

    # 4. Distance progress ascent
    idx_50, idx_60, idx_70, idx_80, idx_90 = get_distance_progress_checkpoints(df, start_idx=lift_off_idx, end_idx=idx_ext)
    
    # 5. Distance progress descent
    idx_50_descent, idx_60_descent, idx_70_descent, idx_80_descent, idx_90_descent = get_distance_progress_checkpoints(df, start_idx=drop_start_idx, end_idx=drop_end_idx)
    

    # Collect all indices and checkpoint names
    front_checkpoints = [
        ('Lift-off', lift_off_idx),
        ('Lift Progress Up (50%)', idx_50),
        ('Lift Progress Up (60%)', idx_60),
        ('Lift Progress Up (70%)', idx_70),
        ('Lift Progress Up (80%)', idx_80),
        ('Lift Progress Up (90%)', idx_90),
        ('Full Extension', idx_ext),
        ('Lift Progress Down (90%)', idx_90_descent),
        ('Lift Progress Down (80%)', idx_80_descent),
        ('Lift Progress Down (70%)', idx_70_descent),
        ('Lift Progress Down (60%)', idx_60_descent),
        ('Lift Progress Down (50%)', idx_50_descent),
        ('Downward Motion End', drop_end_idx)
    ]
    print(f"\nFront checkpoints:")
    pprint(front_checkpoints)
    # Remove duplicates and sort by frame
    seen = set()
    unique_checkpoints = []
    for name, idx in front_checkpoints:
        if idx not in seen:
            unique_checkpoints.append((name, idx))
            seen.add(idx)
    # Build output DataFrame
    out = []
    for name, idx in unique_checkpoints:
        row = df.loc[idx].copy()
        row['checkpoint'] = name
        out.append(row)
    result = pd.DataFrame(out)

    cols = ['timestamp', 'frame_count', 'checkpoint'] + [c for c in df.columns if c not in ['timestamp', 'checkpoint','frame_count']]
    print(f"Upward:\nNearest IDX: \n\tLift-off index: {lift_off_idx},\n\t50 degrees index: {idx_50}, \n\t60 degrees index: {idx_60}, \n\t70 degrees index: {idx_70}, \n\t80 degrees index: {idx_80},\n\t90 degrees index: {idx_90}, \n\tFull extension index: {idx_ext}\n\t")

    print(f"Downward:\nNearest IDX:  \n\t50 degrees index: {idx_50_descent}, \n\t60 degrees index: {idx_60_descent}, \n\t70 degrees index: {idx_70_descent}, \n\t80 degrees index: {idx_80_descent}, \n\t90 degrees index: {idx_90_descent}, \n\tDownward motion end index: {drop_end_idx}\n\t")
    
    return result[cols]



def find_checkpoints_side_view(df: pd.DataFrame, side: str = 'left') -> pd.DataFrame:
    """
    Segments the deadlift into biomechanical checkpoints as defined in the provided table.
    Returns a DataFrame with one row per checkpoint and relevant keypoints with a label for that checkpoint.
    Args:
        df: DataFrame provided after Butterworth filtering.
        side: 'left' or 'right'.
        velocity_threshold: Minimum velocity for lift-off detection.
    Returns:
        Dataframe
    """
    
    # keypoint values
    wrist_y, _, _, shoulder_y, _ = get_keypoint_values(df, side=side)

    # 1. liftoff: first significant upward movement of wrist
    lift_off_idx = get_start_velocity_idx(shoulder_y, velocity_threshold=.5)
    # print(f'\nKnee Y: {knee_y[lift_off_idx]}, Ankle Y: {ankle_y[lift_off_idx]}, Wrist Y: {wrist_y[lift_off_idx]}\n')
    

    # 2. Full Extension: hip angle > 180°
    hip_angles = calculate_hip_angle(df, side=side)
    idx_ext = hip_angles[hip_angles > 180].index.min()
    if pd.isna(idx_ext):
        idx_ext = hip_angles.idxmax()

    print(f'Extension index: {idx_ext}')

    # 3. Downward motion after full extension
    drop_start_idx, drop_end_idx = get_downward_velocity_bounds(shoulder_y, ext_idx=idx_ext, velocity_threshold=0.2, stop_threshold=0.2)

    # 4. Slope indexes on ascent
    idx_120, idx_130, idx_140, idx_150, idx_160 = get_torso_slope_checkpoints(df, side=side, angle_thresholds=(120, 130, 140, 150, 160), start_idx=lift_off_idx, end_idx=idx_ext)

    # 5. Slope indexes on descent
    idx_120_descent, idx_130_descent, idx_140_descent, idx_150_descent, idx_160_descent = get_torso_slope_checkpoints(df, side=side, angle_thresholds=(120, 130, 140, 150, 160), start_idx=idx_ext, end_idx=drop_end_idx) 



    print(f"Upward:\nNearest IDX: \n\tLift-off index: {lift_off_idx}, \n\t120 Degrees index: {idx_120}, \n\t130 degrees index: {idx_130}, \n\t140 degrees index: {idx_140}, \n\t150 degrees index: {idx_150}, \n\t160 degrees index: {idx_160}, \n\tFull extension index: {idx_ext}\n\t")

    print(f"Downward:\nNearest IDX: \n\t120 Degrees index: {idx_120_descent}, \n\t130 degrees index: {idx_130_descent}, \n\t140 degrees index: {idx_140_descent}, \n\t150 degrees index: {idx_150_descent}, \n\t160 degrees index: {idx_160_descent}, \n\tDownward motion end index: {drop_end_idx}\n\t")
    
    # Collect all indices and checkpoint names
    side_checkpoints = [
        ('Lift-off', lift_off_idx),
        ('Torso Progress (120 degrees)', idx_120),
        ('Torso Progress (130 degrees)', idx_130),
        ('Torso Progress (140 degrees)', idx_140),
        ('Torso Progress (150 degrees)', idx_150),
        ('Torso Progress (160 degrees)', idx_160),
        ('Full Extension', idx_ext),
        ('Torso Descent (160 degrees)', idx_160_descent),
        ('Torso Descent (150 degrees)', idx_150_descent),
        ('Torso Descent (140 degrees)', idx_140_descent),
        ('Torso Descent (130 degrees)', idx_130_descent),
        ('Torso Descent (120 degrees)', idx_120_descent),
        ('Downward Motion End', drop_end_idx)
    ]
    # Remove duplicates and sort by frame
    seen = set()
    unique_checkpoints = []
    for name, idx in side_checkpoints:
        if idx not in seen:
            unique_checkpoints.append((name, idx))
            seen.add(idx)
    # Build output DataFrame
    out = []
    for name, idx in unique_checkpoints:
        row = df.loc[idx].copy()
        row['checkpoint'] = name
        out.append(row)
    result = pd.DataFrame(out)


    cols = ['timestamp', 'frame_count', 'checkpoint'] + [c for c in df.columns if c not in ['timestamp', 'checkpoint','frame_count']]
    return result[cols]


