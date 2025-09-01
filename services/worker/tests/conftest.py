import sys
from pathlib import Path

# Ensure the worker root is on the import path for tests
sys.path.append(str(Path(__file__).resolve().parents[1]))
