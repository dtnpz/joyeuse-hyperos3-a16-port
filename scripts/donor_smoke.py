#!/usr/bin/env python3
import hashlib
import json
import sys
import zipfile
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit("usage: donor_smoke.py CONFIG_JSON DONOR_ZIP")

cfg = json.loads(Path(sys.argv[1]).read_text())
archive = Path(sys.argv[2])

h = hashlib.md5()
sha = hashlib.sha256()
size = 0
with archive.open("rb") as f:
    for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
        size += len(chunk)
        h.update(chunk)
        sha.update(chunk)

actual_md5 = h.hexdigest()
if actual_md5.lower() != cfg["md5"].lower():
    raise SystemExit(f"MD5 mismatch: expected {cfg['md5']} got {actual_md5}")

with zipfile.ZipFile(archive) as z:
    names = z.namelist()
    interesting = [n for n in names if n in {
        "payload.bin",
        "payload_properties.txt",
        "META-INF/com/android/metadata",
        "META-INF/com/google/android/updater-script"
    }]
    if "payload.bin" not in names:
        raise SystemExit("OTA does not contain payload.bin")

    metadata = ""
    if "META-INF/com/android/metadata" in names:
        metadata = z.read("META-INF/com/android/metadata").decode("utf-8", "replace")

manifest = {
    "device": cfg["device"],
    "codename": cfg["codename"],
    "hyperos": cfg["hyperos"],
    "android": cfg["android"],
    "filename": archive.name,
    "size_bytes": size,
    "md5": actual_md5,
    "sha256": sha.hexdigest(),
    "ota_entries": interesting,
    "metadata": metadata.splitlines(),
}
Path("donor-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
