# FitFeedback

FitFeedback is an end-to-end application for automated deadlift analysis and feedback using computer vision, pose estimation, and LLM-based report generation. The system processes video input, extracts biomechanical metrics, and generates structured feedback for athletes and coaches.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Component Overview](#component-overview)
- [Troubleshooting](#troubleshooting)

## Features
- Video upload and pose estimation (YOLO or similar models)
- Extraction of key biomechanical metrics (angles, distances, symmetry)
- Multi-agent LLM feedback pipeline (CrewAI)
- Customizable knowledge base (CSV, text, PDF, etc.)
- Streamlit web interface for user interaction and visualization

## Installation

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd FitFeedback/fitfeedback
   ```

2. **Install Python (recommended: 3.10 or 3.11):**
   Ensure you are using a supported Python version. Python 3.13 is not recommended.

3. **Create and activate a virtual environment:**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. **Install requirements:**
   - If using pip:
     ```sh
     pip install -r requirements.txt
     ```
   - If using [uv](https://github.com/astral-sh/uv):
     ```sh
     uv pip install -r requirements.txt
     ```
   - Install additional models as needed:
     ```sh
     python -m spacy download en_core_web_sm
     ```

5. **Download any required model weights** (e.g., YOLO pose weights) and place them in the appropriate directory as specified in the code/config.

## Running the Application

From the project root (where `main.py` is located), run:

```sh
python main.py
```

This will set up the environment and launch the Streamlit web application. You can then access the app in your browser (default: http://localhost:8501 or the port specified in the logs).

## Project Structure

```
fitfeedback/
├── main.py                # Entry point for launching the app
├── src/
│   ├── app/               # Streamlit UI and user interaction
│   ├── fitfeedback/       # Core analysis, metrics, and pipeline code
│   └── fitfeedback_flow/  # CrewAI orchestration and agent/task configs
├── analysis_and_evaluation/LLM/ # LLM evaluation scripts
├── outputs/               # Processed results and generated images
├── LLM_Logs/              # Logs from LLM agent runs
├── requirements.txt       # Python dependencies
└── ...
```

## Component Overview

- **main.py**: Sets up the environment and launches the Streamlit app.
- **src/app/app.py**: Streamlit web interface for video upload, running analysis, and displaying results.
- **src/fitfeedback/main.py**: Main pipeline for video processing, pose estimation, and metric extraction.
- **src/fitfeedback/metrics/**: Utility functions for calculating biomechanical angles, distances, and other metrics.
- **src/fitfeedback_flow/**: CrewAI orchestration, including agent and task definitions, knowledge source configuration, and multi-agent workflow logic.
- **analysis_and_evaluation/LLM/**: Scripts for evaluating and comparing LLM outputs.
- **outputs/**: Stores processed CSVs, checkpoint images, and other results.
- **LLM_Logs/**: Stores logs and outputs from LLM agent runs for traceability.

## Troubleshooting

- **Port already in use**: If you see an error about the port being in use, kill the existing process or run Streamlit on a different port.
- **Missing models**: If you get errors about missing models (e.g., `en_core_web_sm`), install them as shown above.
- **ModuleNotFoundError**: Ensure your virtual environment is activated and all requirements are installed.
- **Zombie processes**: Always stop the app with `Ctrl+C` (not `Ctrl+Z`). If you have many zombie processes, restart your terminal or use `kill` to clean them up.

## Acknowledgements
- Built with [Streamlit](https://streamlit.io/), [spaCy](https://spacy.io/), [YOLO](https://github.com/ultralytics/yolov5), and [CrewAI](https://crewai.com/).
