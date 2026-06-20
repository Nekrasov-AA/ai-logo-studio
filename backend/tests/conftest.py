import sys
from pathlib import Path

# Ensure `backend/` is on sys.path so `from app.services...` imports work
# when pytest is invoked from the repo root or any subdirectory.
sys.path.insert(0, str(Path(__file__).parent.parent))
