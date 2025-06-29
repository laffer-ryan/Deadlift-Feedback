import os
import numpy as np
import pandas as pd
import cv2
from fitfeedback.acquisition.video_loader import load_video, get_video_fps, read_frame, release_video
from fitfeedback.pose_estimation.yolo_pose import load_yolo_model, estimate_pose, map_keypoints_and_confidence
from fitfeedback.pre_processing.confidence_filter import apply_confidence_threshold
from fitfeedback.pre_processing.spline_interpolation import spline_interpolation
from fitfeedback.pre_processing.butterworth_filter import butterworth_filter
from fitfeedback.data_formatting.tabular import split_keypoint_columns
from fitfeedback.segmentation.checkpoint import get_checkpoints
from fitfeedback.segmentation.side_facing import determine_view
from fitfeedback.metrics.metric_calculations import calculate_angles_and_distances
from fitfeedback.post_processing.convert_yolo_captures import convert_yolo_captures_to_pipeline
import shutil
from pprint import pprint

MODEL_PATH = 'yolo11m-pose.pt'
OUTPUT_DIR = 'outputs'
KNOWLEDGE_DIR = 'src/fitfeedback_flow/knowledge'
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR, exist_ok=True)
output_image_dir = os.path.join(OUTPUT_DIR, 'videos')
os.makedirs(output_image_dir, exist_ok=True)

def empty_directory(dir_path: str):
    for entry in os.listdir(dir_path):
        fullpath = os.path.join(dir_path, entry)
        if os.path.isfile(fullpath) or os.path.islink(fullpath):
            os.remove(fullpath)
        elif os.path.isdir(fullpath):
            shutil.rmtree(fullpath)

def run_pipeline(video_path: str) -> str:
    """
    Run full pose estimation + preprocessing pipeline on a video.

    Returns the path to the final processed CSV file.
    """
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    empty_directory(output_image_dir)

    # Load video and model
    cap = load_video(video_path)
    fps = get_video_fps(cap)
    frame_time = 1 / fps
    model = load_yolo_model(MODEL_PATH)

    results = []
    frame_count = 0
    frame_dict = {}

    while True:
        ret, frame = read_frame(cap)
        if not ret:
            break
        frame_count += 1
        keypoints, confidence = estimate_pose(model, frame)
        if keypoints is not None:
            orig_height, orig_width = frame.shape[:2]
            results.append({
                'timestamp': frame_time * frame_count,
                'video_name': video_name,
                'frame_count': frame_count,
                'keypoints': keypoints,
                'confidence': confidence,
                'orig_width': orig_width,
                'orig_height': orig_height,
            })
            frame_dict[frame_count] = frame.copy()
    release_video(cap)
    print(f"Processed {len(results)} frames.")

    # Convert to dataframe
    df = pd.DataFrame(results)
    df = map_keypoints_and_confidence(df)
    df = split_keypoint_columns(df)
    df = apply_confidence_threshold(df, threshold=0.50)
    spline_df = spline_interpolation(df)
    spline_df = convert_yolo_captures_to_pipeline(spline_df)
    butter_df = butterworth_filter(spline_df)
    df = convert_yolo_captures_to_pipeline(butter_df)
    # Determine view and get metrics
    direction = determine_view(df)
    df = get_checkpoints(df, side=direction)
    with pd.option_context('display.max_columns', None, 'display.width', None):
        [print(df[col]) for col in df.columns]
    df = df.replace(0, np.nan)

    df = calculate_angles_and_distances(df, side=direction)

    # Only until Full Extension checkpoint
    full_ext_indices = df[df['checkpoint'] == 'Full Extension'].index
    if not full_ext_indices.empty:
        last_index = full_ext_indices[0]
        df = df.loc[:last_index]

    # Save images at checkpoints

    if 'frame_count' in df.columns:
        checkpoint_rows = df[['frame_count', 'checkpoint']].drop_duplicates()
        for _, row in checkpoint_rows.iterrows():
            fc = row['frame_count']
            checkpoint_label = str(row['checkpoint'])
            if fc in frame_dict:
                img = frame_dict[fc].copy()
                cv2.putText(img, checkpoint_label, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, .8, (0, 255, 0), 2, cv2.LINE_AA)
                keypoints_row = df[df['frame_count'] == fc]
                if not keypoints_row.empty:
                    keypoint_names = [
                        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
                        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
                        "left_wrist", "right_wrist", "left_hip", "right_hip",
                        "left_knee", "right_knee", "left_ankle", "right_ankle"
                    ]
                    keypoints = []
                    for name in keypoint_names:
                        x_col = f"{name}_x"
                        y_col = f"{name}_y"
                        if x_col in keypoints_row.columns and y_col in keypoints_row.columns:
                            x = keypoints_row.iloc[0][x_col]
                            y = keypoints_row.iloc[0][y_col]
                            if not (pd.isna(x) or pd.isna(y)):
                                keypoints.append((x, y))
                            else:
                                keypoints.append((0, 0))
                        else:
                            keypoints.append((0, 0))
                    # Draw based on direction
                    if direction == 'front':
                        skeleton = [
                            (5, 7), (7, 9), (6, 8), (8, 10), # arms
                            (5, 6), (5, 11), (6, 12), # shoulders to hips
                            (11, 12), (11, 13), (13, 15), (12, 14), (14, 16) # legs
                        ]
                        draw_keypoints_and_lines(img, keypoints, skeleton, mode='all')

                    elif direction == 'left':
                        # Include left eye and nose in the indices and skeleton
                        left_indices = [0, 1, 5, 7, 9, 11, 13, 15]  # nose=0, left_eye=1
                        left_skeleton = [
                            (5, 7), (7, 9), (5, 11), (11, 13), (13, 15),
                            (0, 1), (1, 5), (0, 5)  # nose to left_eye, left_eye to left_shoulder, nose to left_shoulder
                        ]
                        draw_keypoints_and_lines(img, keypoints, left_skeleton, mode='left', indices=left_indices)

                    elif direction == 'right':
                        # Include right eye and nose in the indices and skeleton
                        right_indices = [0, 2, 6, 8, 10, 12, 14, 16]  # nose=0, right_eye=2
                        right_skeleton = [
                            (6, 8), (8, 10), (6, 12), (12, 14), (14, 16),
                            (0, 2), (2, 6), (0, 6)  # nose to right_eye, right_eye to right_shoulder, nose to right_shoulder
                        ]
                        draw_keypoints_and_lines(img, keypoints, right_skeleton, mode='right', indices=right_indices)
                img_path = os.path.join(output_image_dir, f"{video_name}_checkpoint_{fc}.jpg")
                cv2.imwrite(img_path, img)




    if direction == 'front':
        df = df[['checkpoint', 'left_to_right_shoulder_slope', 'left_right_wrist_slope', 'head_tilt_slope', 'normalised_shoulder_distance', 'normalised_wrist_difference', 'normalised_ankle_difference', 'normalised_knee_distance', 'right_knee_lateral_distance_from_center', 'left_knee_lateral_distance_from_center', 'right_ankle_lateral_distance_from_center', 'left_ankle_lateral_distance_from_center', 'right_wrist_lateral_distance_from_center', 'left_wrist_lateral_distance_from_center']]
    elif direction == 'left':
        df = df[['checkpoint', 'bar_distance_from_body', 'left_elbow_angle', 'lower_left_wrist_angle', 'upper_left_wrist_angle', 'neck_angle_left', 'posterior_chain_left', 'left_knee_angle', 'left_hip_angle']]
    elif direction == 'right':
        df = df[['checkpoint', 'bar_distance_from_body', 'right_elbow_angle', 'lower_right_wrist_angle', 'upper_right_wrist_angle', 'neck_angle_right', 'posterior_chain_right', 'right_knee_angle', 'right_hip_angle']]

    # Save final output
    output_csv_path = os.path.join(OUTPUT_DIR, f"processed_pipeline.csv")
    df.to_csv(output_csv_path, index=False)

    write_knowledge(KNOWLEDGE_DIR, df)


    return output_csv_path, output_image_dir, direction

def draw_keypoints_and_lines(img, keypoints, connections, color=(0, 255, 255), radius=2, thickness=2, mode='all', indices=None):
    """
    Draws keypoints and lines (skeleton) on the image.
    mode: 'all', 'left', or 'right'
    indices: list of keypoint indices to draw (for left/right)
    """
    if mode == 'all':
        # Draw all lines
        for start_idx, end_idx in connections:
            pt1 = tuple(map(int, keypoints[start_idx]))
            pt2 = tuple(map(int, keypoints[end_idx]))
            cv2.line(img, pt1, pt2, color, thickness)
        # Draw all keypoints
        for x, y in keypoints:
            cv2.circle(img, (int(x), int(y)), radius, (0, 0, 255), -1)
    else:
        # Only draw lines and keypoints for specified indices
        if indices is None:
            return
        # Draw lines
        for start_idx, end_idx in connections:
            if start_idx in indices and end_idx in indices:
                pt1 = tuple(map(int, keypoints[start_idx]))
                pt2 = tuple(map(int, keypoints[end_idx]))
                cv2.line(img, pt1, pt2, color, thickness)
        # Draw keypoints
        for idx in indices:
            x, y = keypoints[idx]
            cv2.circle(img, (int(x), int(y)), radius, (0, 0, 255), -1)


def write_knowledge(knowledge_dir: str, df: pd.DataFrame):
    """
    Writes the processed DataFrame to various formats in the knowledge directory.
    """
    if not os.path.exists(knowledge_dir):
        os.makedirs(knowledge_dir)

    df_copy = df.copy()

    first_three_rows = df_copy.iloc[:3]
    rest_of_df = df_copy.iloc[3:]

    first_three_rows.to_csv(os.path.join(knowledge_dir, 'setup_processed_pipeline.csv'), index=False)
    first_three_rows.to_json(os.path.join(knowledge_dir, 'setup_processed_pipeline.json'))
    first_three_rows.to_markdown(os.path.join(knowledge_dir, 'setup_processed_pipeline.md'))
    first_three_rows.to_excel(os.path.join(knowledge_dir, 'setup_processed_pipeline.xlsx'))

    rest_of_df.to_csv(os.path.join(knowledge_dir, 'pull_processed_pipeline.csv'), index=False)
    rest_of_df.to_json(os.path.join(knowledge_dir, 'pull_processed_pipeline.json'))
    rest_of_df.to_markdown(os.path.join(knowledge_dir, 'pull_processed_pipeline.md'))
    rest_of_df.to_excel(os.path.join(knowledge_dir, 'pull_processed_pipeline.xlsx'))

    df_copy.to_csv(os.path.join(knowledge_dir, 'processed_pipeline.csv'), index=False)
    df_copy.to_json(os.path.join(knowledge_dir, 'processed_pipeline.json'))
    df_copy.to_markdown(os.path.join(knowledge_dir, 'processed_pipeline.md'), index=False)
    df_copy.to_excel(os.path.join(knowledge_dir, 'processed_pipeline.xlsx'), index=False)
    print(f"Knowledge written to {knowledge_dir}")