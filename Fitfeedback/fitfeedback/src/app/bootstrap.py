# Changing streamlit Python path configurations

def configure_python_path():
    """
    Ensures the src directory is in sys.path for module imports.
    """
    import sys
    import os

    # Remove unwanted paths
    sys.path = [p for p in sys.path if not p.endswith("src/app") and not p.endswith("src/app/app.py")]

    # Dynamically find src directory
    app_dir = os.path.dirname(os.path.abspath(__file__))     # src/app
    src_dir = os.path.abspath(os.path.join(app_dir, ".."))   # src

    # Inject src if not already in sys.path
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)