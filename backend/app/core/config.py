from pathlib import Path
import sys

# Define BASE_DIR as the project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))
print(f"BASE_DIR set to: {BASE_DIR}")