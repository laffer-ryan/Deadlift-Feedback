# app/app.py
import streamlit as st
import pandas as pd
from pathlib import Path

# Ensure the src directory is in sys.path for module imports
from bootstrap import configure_python_path
configure_python_path()


from app.utils import extract_number
from fitfeedback import run_pipeline
from fitfeedback_flow import run_deadlift_flow



TEMP_DIR = Path("temp_videos")
TEMP_DIR.mkdir(exist_ok=True)


st.set_page_config(page_title="FitFeedback App", layout="centered")
st.title("🏋️‍♂️ FitFeedback: Deadlift Analysis")

video_file = st.file_uploader("Upload a deadlift video", type=["mp4", "mov", "avi"])

if video_file:
    video_path = TEMP_DIR / video_file.name
    with open(video_path, "wb") as f:
        f.write(video_file.read())

    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.video(str(video_path), muted=True, width=300)
        run_analysis = st.button("Run Full Analysis")

    if 'run_analysis' in locals() and run_analysis:
        with st.spinner("Running inference and generating feedback..."):
            processed_data_path, images_dir, view = run_pipeline(str(video_path))
            df = pd.read_csv(processed_data_path)

                       
        st.success("✅ Analysis Complete!")
        st.markdown("### 🧠 Feedback Summary")
        st.dataframe(df.head(100))

        # Show images in grid (full width)
        if images_dir:
            import re
            image_files = sorted(Path(images_dir).glob("*.jpg"), key=extract_number)
            cols = st.columns(3)
            for i, img_path in enumerate(image_files):
                with cols[i % 3]:
                    st.image(str(img_path), caption=f"Frame {i + 1}")

        video_name = video_file.name
        input_data = {
            "topic": "deadlift",
            "view_direction": view.lower()
        }

        with st.spinner("Generating LLM feedback…"):
            feedback = run_deadlift_flow(input_data, video_name=video_name,)      

        st.markdown("### 🤖 Deadlift Feedback")
        st.write(feedback)
