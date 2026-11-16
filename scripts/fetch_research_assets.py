"""Fetch immutable public synthetic assets and verify bytes before installation."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def fetch(verify_only=False):
    manifest = json.loads((ROOT / "configs/research-assets.json").read_text())
    if manifest["repository"] != "Simo-Mesbahi/Fraud-risk-model-optimized":
        raise ValueError("Unexpected asset repository.")
    for entry in manifest["assets"]:
        destination = (ROOT / entry["path"]).resolve()
        if ROOT not in destination.parents:
            raise ValueError("Asset path escapes the project.")
        if (
            destination.is_file()
            and destination.stat().st_size == entry["bytes"]
            and digest(destination) == entry["sha256"]
        ):
            print("Verified", entry["name"], flush=True)
            continue
        if verify_only:
            raise RuntimeError("Missing or invalid asset: " + entry["name"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".download")
        url = (
            "https://github.com/"
            + manifest["repository"]
            + "/releases/download/"
            + urllib.parse.quote(manifest["release_tag"], safe="")
            + "/"
            + urllib.parse.quote(entry["name"], safe="")
        )
        for attempt in range(3):
            try:
                request = urllib.request.Request(
                    url, headers={"User-Agent": "fraud-research-asset-builder/1.0"}
                )
                with (
                    urllib.request.urlopen(request, timeout=45) as response,
                    temporary.open("wb") as file,
                ):
                    received = 0
                    while chunk := response.read(1024 * 1024):
                        received += len(chunk)
                        if received > entry["bytes"]:
                            raise RuntimeError("Asset exceeds the reviewed size.")
                        file.write(chunk)
                if (
                    temporary.stat().st_size != entry["bytes"]
                    or digest(temporary) != entry["sha256"]
                ):
                    raise RuntimeError("Asset checksum mismatch.")
                temporary.replace(destination)
                print("Installed verified asset", entry["name"], flush=True)
                break
            except Exception:
                temporary.unlink(missing_ok=True)
                if attempt == 2:
                    raise
                time.sleep(2**attempt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    fetch(parser.parse_args().verify_only)
