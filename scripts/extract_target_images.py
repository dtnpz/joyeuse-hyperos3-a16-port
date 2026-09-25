#!/usr/bin/env python3
import json
import shutil
import sys
import tarfile
from pathlib import Path

if len(sys.argv) != 4:
    raise SystemExit("usage: extract_target_images.py CONFIG_JSON TARGET_TGZ OUT_DIR")

cfg = json.loads(Path(sys.argv[1]).read_text())
archive = Path(sys.argv[2])
out = Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)

wanted = set(cfg["candidate_extract"])
found = {}

with tarfile.open(archive, "r:gz") as tf:
    for member in tf:
        base = Path(member.name).name
        if base not in wanted or not member.isfile():
            continue
        if base in found:
            raise SystemExit(f"duplicate target image basename in archive: {base}")
        src = tf.extractfile(member)
        if src is None:
            raise SystemExit(f"unable to read {member.name}")
        dst = out / base
        with dst.open("wb") as f:
            shutil.copyfileobj(src, f, length=8 * 1024 * 1024)
        found[base] = member.name
        print(f"extracted {member.name} -> {dst} ({dst.stat().st_size} bytes)")

missing = wanted - set(found)
if missing:
    raise SystemExit("missing target image(s): " + ", ".join(sorted(missing)))

Path("target-extract-map.json").write_text(
    json.dumps({"archive": archive.name, "images": found}, indent=2) + "\n"
)
