#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
from pathlib import Path

out = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
rows = []
for p in sorted(out.glob("*.img")):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    desc = subprocess.check_output(["file", "-b", str(p)], text=True).strip()
    lower = desc.lower()
    if "erofs" in lower:
        fs = "erofs"
    elif "ext4" in lower or "ext2" in lower or "ext3" in lower:
        fs = "ext4-family"
    elif "f2fs" in lower:
        fs = "f2fs"
    else:
        fs = "unknown"
    rows.append({
        "name": p.name,
        "bytes": p.stat().st_size,
        "sha256": h.hexdigest(),
        "filesystem": fs,
        "file_output": desc,
    })

if not rows:
    raise SystemExit("no extracted .img files found")

manifest = {"images": rows}
Path("donor-image-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
