# main.py
import os
import sys


src_path = os.path.join(os.path.dirname(__file__), "src")
os.environ["PYTHONPATH"] = src_path
print(f"Setting PYTHONPATH to: {src_path}")

os.execvp("streamlit", ["streamlit", "run", "src/app/app.py"])