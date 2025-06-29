# Utility functions 
import re


def extract_number(path):
    """ Used to ensure checkpoints are listed in the correct order."""
    match = re.search(r"checkpoint_(\d+)\.jpg", path.name)
    return int(match.group(1)) if match else float('inf')