#!/usr/bin/env python
"""
Launcher for Gryphon with AI.

This script sets up the environment and launches Gryphon with AI features enabled.
"""
import sys
import os
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.absolute()

# Add project root to Python path so gryphon_ai can be found
sys.path.insert(0, str(project_root))

# Import gryphon_ai to ensure it's available when gui_manager imports it
import gryphon_ai

# Change to gryphon_ai/gryphon_source/python directory
gryphon_python = project_root / "gryphon_ai" / "gryphon_source" / "python"
if not gryphon_python.exists():
    print("ERROR: gryphon_ai/gryphon_source/python directory not found!")
    print("Please make sure Gryphon source is included in the repository.")
    sys.exit(1)

# Add to path
sys.path.insert(0, str(gryphon_python))

# Change directory
os.chdir(gryphon_python)

# Run Gryphon's mp.py as a script
try:
    import runpy
    
    # Run mp.py as __main__ so the if __name__ == "__main__" block executes
    runpy.run_path(str(gryphon_python / "mp.py"), run_name="__main__")
    
except ImportError as e:
    print(f"ERROR: Could not import Gryphon: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except KeyboardInterrupt:
    print("\nGryphon closed by user.")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
