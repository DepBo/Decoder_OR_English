"""
Top-level run_research_validation.py wrapper
Delegates to Dataset_Paper_DecoderOr/run_research_validation.py
"""
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUB_DIR = ROOT / "Dataset_Paper_DecoderOr"
SUB_SCRIPT = SUB_DIR / "run_research_validation.py"

if __name__ == "__main__":
    venv_py = SUB_DIR / ".venv" / "Scripts" / "python.exe"
    py_exec = str(venv_py) if venv_py.exists() else sys.executable
    proc = subprocess.run([py_exec, str(SUB_SCRIPT)] + sys.argv[1:], cwd=str(SUB_DIR))
    sys.exit(proc.returncode)
