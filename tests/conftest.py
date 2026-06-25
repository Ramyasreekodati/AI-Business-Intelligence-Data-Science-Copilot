# Configure pytest to include the project root in PYTHONPATH
import sys
import os

# Add the directory containing the 'project' package to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
