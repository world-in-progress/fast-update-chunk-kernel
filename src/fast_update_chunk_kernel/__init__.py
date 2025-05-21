import os
from pathlib import Path
from .merger import Merger

def check_progress(workspace_dir: str):
    workspace_path = Path(workspace_dir)
    
    # Get grid num
    grid_num = 0.0
    try:
        grid_num_file = list(workspace_path.glob('grid_num_*'))[0]
        if not grid_num_file:
            return 0.0 # No grid_num file found, so progress is 0
        grid_num = float(grid_num_file.name.split('_')[-1])
    except (IOError, ValueError):
        return 0.0 # Error reading or parsing file, or file not found

    if grid_num <= 0.0:
        return 0.0

    # Iterate through subdirectories in the 'output' directory to count completed processing
    completed_count = 0.0
    output_dir_path = workspace_path / 'output'

    if output_dir_path.is_dir():
        for item in output_dir_path.iterdir():
            # Check if the item is a directory (representing a grid's output folder)
            if item.is_dir():
                done_file = item / 'done'
                if done_file.exists() and done_file.is_file():
                    completed_count += 1.0

    return completed_count / grid_num