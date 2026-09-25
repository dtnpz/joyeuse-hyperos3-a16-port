#!/usr/bin/env python3
import hashlib
import json
import sys
import tarfile
from pathlib import Path

if len(sys.argv) != 3:
    raise SystemExit("usage: target_smoke.py CONFIG_JSON TARGET_TGZ")

cfg=json.loads(Path(sys.argv[1]).read_text())
archive=Path(sys.argv[2])
h=hashlib.md5(); sha=hashlib.sha256(); size=0
with archive.open("rb") as f:
    for chunk in iter(lambda:f.read(8*1024*1024), b""):
        size += len(chunk); h.update(chunk); sha.update(chunk)
if h.hexdigest().lower() != cfg["md5"].lower():
    raise SystemExit(f"MD5 mismatch: expected {cfg['md5']} got {h.hexdigest()}")

with tarfile.open(archive, "r:gz") as t:
    names=t.getnames()
    selected=[n for n in names if Path(n).name in set(cfg["candidate_extract"])]
    if not any(Path(n).name=="vendor.img" for n in names):
        raise SystemExit("fastboot package does not contain vendor.img")

manifest={
    "device":cfg["device"],"codename":cfg["codename"],"miui":cfg["miui"],
    "android":cfg["android"],"filename":archive.name,"size_bytes":size,
    "md5":h.hexdigest(),"sha256":sha.hexdigest(),"candidate_images":selected
}
Path("target-stock-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps(manifest,indent=2))
