import cv2

def load_video(video_path):
    """Load a video and return the video capture object."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Unable to open video: {video_path}")
    return cap

def get_video_fps(cap):
    """Get the frames per second (FPS) of the video."""
    return cap.get(cv2.CAP_PROP_FPS)

def read_frame(cap):
    """Read a single frame from the video."""
    ret, frame = cap.read()
    return ret, frame

def release_video(cap):
    """Release the video capture object."""
    cap.release()
