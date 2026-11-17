"""Resolve role-specific, hash-checked locks from the recorded tested versions."""
import os
import subprocess
import sys
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def demo_lock(root=ROOT):
    """Union tested role locks, requiring consistent versions and dependency hashes."""
    packages = {}
    for role in ("api", "frontend"):
        name = None
        for line in (root / f"requirements/{role}.lock").read_text().splitlines():
            match = re.match(r"^([a-zA-Z0-9_.-]+)==([^\s;]+)", line)
            if match:
                name, version = match.groups()
                if name in packages and packages[name][0] != version:
                    raise ValueError("Conflicting role-lock versions for " + name)
                packages.setdefault(name, (version, set()))
            elif line.lstrip().startswith("--hash=") and name:
                packages[name][1].add(line.strip().removesuffix("\\").strip())
    lines = ["# Generated from the tested api.lock and frontend.lock.",
             "# Regenerate: python scripts/lock_dependencies.py --demo-only", ""]
    for name, (version, hashes) in sorted(packages.items()):
        if not hashes:
            raise ValueError("Missing dependency hashes for " + name)
        record = [f"{name}=={version}", *["    " + value for value in sorted(hashes)]]
        lines.append(" \\\n".join(record))
    (root / "requirements/demo.lock").write_text("\n".join(lines) + "\n")


def main():
    if "--demo-only" in sys.argv:
        demo_lock()
        return
    for role in ("api","frontend","dev"):
        subprocess.run([sys.executable,"-m","piptools","compile","--generate-hashes","--allow-unsafe","--strip-extras",
                        "--no-emit-index-url","--no-emit-trusted-host","-c","requirements/tested.constraints",
                        "--output-file",f"requirements/{role}.lock",f"requirements/{role}.in"],
                       cwd=ROOT,check=True,env={**os.environ,"CUSTOM_COMPILE_COMMAND":"python scripts/lock_dependencies.py"})
    demo_lock()


if __name__ == "__main__":
    main()
