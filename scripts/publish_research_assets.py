"""Publish reviewed synthetic assets once, using the workflow's scoped GitHub token."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / "configs/research-assets.json").read_text())
    repository = manifest["repository"]
    if os.environ.get("GITHUB_REPOSITORY") != repository:
        raise RuntimeError("Publishing is restricted to the project's own repository.")
    tag = manifest["release_tag"]
    exists = False
    try:
        with urllib.request.urlopen(
            f"https://api.github.com/repos/{repository}/releases/tags/{tag}", timeout=30
        ) as response:
            json.load(response)
        exists = True
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
    if exists:
        subprocess.run([sys.executable, "scripts/fetch_research_assets.py"], cwd=ROOT, check=True)
        return
    subprocess.run([sys.executable, "scripts/build_research_assets.py", "--rebuild"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/fetch_research_assets.py", "--verify-only"], cwd=ROOT, check=True)
    with tempfile.TemporaryDirectory() as temporary:
        assets = []
        for item in manifest["assets"]:
            destination = Path(temporary) / item["name"]
            shutil.copyfile(ROOT / item["path"], destination)
            assets.append(str(destination))
        subprocess.run([
            "gh", "release", "create", tag, *assets,
            "--repo", repository, "--target", os.environ["GITHUB_SHA"],
            "--title", "Synthetic longitudinal research corpus v4",
            "--notes-file", "docs/research-data-release.md", "--prerelease",
        ], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
