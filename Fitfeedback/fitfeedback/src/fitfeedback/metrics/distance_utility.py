import math

def get_point(row, name):
    return row[f"{name}_x"], row[f"{name}_y"]

def calculate_pixel_difference(a, b) -> float:
    """Helper to calculate Euclidean distance between two 2D points."""
    return math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)

def mid_hip_x(row):
    left_hip_x, _ = get_point(row, 'left_hip')
    right_hip_x, _ = get_point(row, 'right_hip')
    return (left_hip_x + right_hip_x) / 2

def hip_distance(row) -> float:
    return calculate_pixel_difference(get_point(row, 'left_hip'), get_point(row, 'right_hip'))

def normalised_distance(row, point1: str, point2: str) -> float:
    """Calculate distance between two keypoints normalized by hip width."""
    hip_dist = hip_distance(row)
    if hip_dist == 0:  # Prevent divide by zero
        return 0.0
    return calculate_pixel_difference(get_point(row, point1), get_point(row, point2)) / hip_dist

def wrist_difference(row) -> float:
    return normalised_distance(row, 'left_wrist', 'right_wrist')

def ankle_difference(row) -> float:
    return normalised_distance(row, 'left_ankle', 'right_ankle')

def shoulder_distance(row) -> float:
    return normalised_distance(row, 'left_shoulder', 'right_shoulder')

def knee_distance(row) -> float:
    return normalised_distance(row, 'left_knee', 'right_knee')

def left_knee_lateral_distance(row):
    mid_hip_x = (row['left_hip_x'] + row['right_hip_x']) / 2
    dist = abs(row['left_knee_x'] - mid_hip_x)
    return dist / hip_distance(row)

def right_knee_lateral_distance(row):
    mid_hip_x = (row['left_hip_x'] + row['right_hip_x']) / 2
    dist = abs(row['right_knee_x'] - mid_hip_x)
    return dist / hip_distance(row)

def left_ankle_lateral_distance(row):
    mid_hip_x = (row['left_hip_x'] + row['right_hip_x']) / 2
    dist = abs(row['left_ankle_x'] - mid_hip_x)
    return dist / hip_distance(row)

def right_ankle_lateral_distance(row):
    mid_hip_x = (row['left_hip_x'] + row['right_hip_x']) / 2
    dist = abs(row['right_ankle_x'] - mid_hip_x)
    return dist / hip_distance(row)

def left_wrist_lateral_distance(row):
    mid_hip_x = (row['left_hip_x'] + row['right_hip_x']) / 2
    dist = abs(row['left_wrist_x'] - mid_hip_x)
    return dist / hip_distance(row)

def right_wrist_lateral_distance(row):
    mid_hip_x = (row['left_hip_x'] + row['right_hip_x']) / 2
    dist = abs(row['right_wrist_x'] - mid_hip_x)
    return dist / hip_distance(row)

def bar_distance_from_body(row, side: str):
    """
    Calculates the perpendicular distance from the {side}_wrist keypoint to the line
    defined by the {side}_ankle and {side}_knee keypoints for a single row.
    """
    x0 = row[f'{side}_wrist_x']
    y0 = row[f'{side}_wrist_y']
    x1 = row[f'{side}_ankle_x']
    y1 = row[f'{side}_ankle_y']
    x2 = row[f'{side}_knee_x']
    y2 = row[f'{side}_knee_y']

    numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    denominator = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
    if denominator < 1e-6:
            return float('nan') 
    distance = numerator / (denominator + 1e-8)
    return distance