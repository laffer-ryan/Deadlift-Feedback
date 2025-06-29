from ultralytics import YOLO
import numpy as np
import pandas as pd


# Keypoint mapping for dataframe
keypoint_name_dict = {
    0: 'nose',
    1: 'left_eye',
    2: 'right_eye',
    3: 'left_ear',
    4: 'right_ear',
    5: 'left_shoulder',
    6: 'right_shoulder',
    7: 'left_elbow',
    8: 'right_elbow',
    9: 'left_wrist',
    10: 'right_wrist',
    11: 'left_hip',
    12: 'right_hip',
    13: 'left_knee',
    14: 'right_knee',
    15: 'left_ankle',
    16: 'right_ankle'
}

def load_yolo_model(model_path):
    """Load the YOLO model for pose estimation."""
    return YOLO(model_path)

def estimate_pose(model, frame):
    """Estimate pose and confidence for a given frame using the YOLO model."""
    try:
        result = model.track(frame, imgsz=(640,640))
        if (
            result
            and hasattr(result[0], "boxes")
            and hasattr(result[0], "keypoints")
            and result[0].boxes is not None
            and result[0].keypoints is not None
            and hasattr(result[0].keypoints, "xy")
            and hasattr(result[0].keypoints, "conf")
            and result[0].keypoints.xy is not None
            and result[0].keypoints.conf is not None
        ):
            boxes = result[0].boxes.xyxy.cpu().numpy()
            keypoints = result[0].keypoints.xy.cpu().numpy()
            scores = result[0].keypoints.conf.cpu().numpy()  # confidence scores for each box
            if len(boxes) == 0:
                return None, None

            # Select the person with the largest bounding box area
            areas = [(box[2] - box[0]) * (box[3] - box[1]) for box in boxes]
            max_area_index = np.argmax(areas)
            return keypoints[max_area_index], scores[max_area_index]
    except AttributeError:
        pass
    except Exception:
        pass
    return None, None


def aggregate_keypoints(keypoints_list):
    """Aggregate keypoints from multiple frames."""
    if not keypoints_list:
        return None
    aggregated = np.mean(keypoints_list, axis=0)
    return aggregated


def map_keypoints_and_confidence(df: pd.DataFrame, keypoint_name_dict: dict = keypoint_name_dict) -> pd.DataFrame:
    """
    Map keypoints and confidence values to their respective names based on the keypoint_name_dict.
    :param df: DataFrame containing raw keypoints and confidence values.
    :param keypoint_name_dict: Dictionary mapping keypoint indices to names.
    :return: Transformed DataFrame with named keypoints and confidence values.
    """
    mapped_data = []
    for _, row in df.iterrows():
        mapped_row = {
            'timestamp': row['timestamp'],
            'frame_count': row['frame_count'],
            'orig_width': row['orig_width'],
            'orig_height': row['orig_height'],
            'video_name': row['video_name'],
        }

        for idx, name in keypoint_name_dict.items():
            if idx < len(row['keypoints']):
                keypoint = row['keypoints'][idx]
                confidence = row['confidence'][idx]
                mapped_row[f'{name}_keypoint'] = keypoint
                mapped_row[f'{name}_confidence'] = confidence

        mapped_data.append(mapped_row)

    return pd.DataFrame(mapped_data)