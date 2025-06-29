import cv2

def draw_keypoints_and_lines(img, keypoints, connections, color=(0, 255, 255), radius=4, thickness=2, mode='all', indices=None):
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
