"""Single import bridge to the unchanged, tested Streamlit core."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
import engine
import coach
import progress_board
