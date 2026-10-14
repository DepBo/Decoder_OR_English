"""
Root audit_results.py wrapper
Delegates to Dataset_Paper_DecoderOr/audit_results.py
"""
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUB_SCRIPT = ROOT / "Dataset_Paper_DecoderOr" / "audit_results.py"

if __name__ == "__main__":
    venv_py = ROOT / "Dataset_Paper_DecoderOr" / ".venv" / "Scripts" / "python.exe"
    py_exec = str(venv_py) if venv_py.exists() else sys.executable
    proc = subprocess.run([py_exec, str(SUB_SCRIPT)] + sys.argv[1:], cwd=str(SUB_SCRIPT.parent))
    sys.exit(proc.returncode)
