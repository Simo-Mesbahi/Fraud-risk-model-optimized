"""Resolve role-specific, hash-checked locks from the recorded tested versions."""
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    for role in ("api","frontend","dev"):
        subprocess.run([sys.executable,"-m","piptools","compile","--generate-hashes","--allow-unsafe","--strip-extras",
                        "--no-emit-index-url","--no-emit-trusted-host","-c","requirements/tested.constraints",
                        "--output-file",f"requirements/{role}.lock",f"requirements/{role}.in"],
                       cwd=ROOT,check=True,env={**os.environ,"CUSTOM_COMPILE_COMMAND":"python scripts/lock_dependencies.py"})


if __name__ == "__main__":
    main()
