
import sys
import os

# Add src/python to path
sys.path.append("c:/2026/Spring/MP+AI/src/python")

try:
    print("Importing gui_manager...")
    import gui_manager
    print("Successfully imported gui_manager")
except ImportError as e:
    print(f"Failed to import gui_manager: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error during import: {e}")
    sys.exit(1)

print("Imports verification passed.")
