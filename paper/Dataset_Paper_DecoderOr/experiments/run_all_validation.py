"""
experiments/run_all_validation.py
---------------------------------
Convenience alias and orchestrator hook pointing to top-level run_research_validation.py.
"""
import sys
import subprocess
from pathlib import Path

EXP_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXP_DIR.parent
MASTER_SCRIPT = REPO_ROOT / "run_research_validation.py"

if __name__ == "__main__":
    venv_py = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    py_exec = str(venv_py) if venv_py.exists() else sys.executable
    proc = subprocess.run([py_exec, str(MASTER_SCRIPT)] + sys.argv[1:], cwd=str(REPO_ROOT))
    sys.exit(proc.returncode)
