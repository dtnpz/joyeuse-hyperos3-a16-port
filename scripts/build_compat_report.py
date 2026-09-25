#!/usr/bin/env python3
import re
import sys
from pathlib import Path

root=Path(sys.argv[1] if len(sys.argv)>1 else "metadata")
out=Path(sys.argv[2] if len(sys.argv)>2 else "compat-report.md")

keys=[
    "ro.build.version.sdk",
    "ro.build.version.release",
    "ro.product.first_api_level",
    "ro.vendor.api_level",
    "ro.board.api_level",
    "ro.vndk.version",
    "ro.treble.enabled",
    "ro.product.cpu.abilist",
]

def props(path):
    d={}
    if not path.exists():
        return d
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("### "):
            continue
        if "=" in line and not line.startswith("#"):
            k,v=line.split("=",1)
            d[k.strip()]=v.strip()
    return d

labels=sorted(p.name for p in root.iterdir() if p.is_dir())
rows=[]
for label in labels:
    p=props(root/label/"properties.txt")
    files=(root/label/"metadata-files.txt")
    vintf=0
    selinux=0
    if files.exists():
        for x in files.read_text(errors="replace").splitlines():
            vintf += "/etc/vintf/" in x
            selinux += "/etc/selinux/" in x
    rows.append((label,p,vintf,selinux))

lines=[
    "# A16 port compatibility preflight",
    "",
    "Generated from read-only mounts of the exact pinned donor/target images.",
    "",
    "| image | Android SDK | release | first API | vendor API | board API | VNDK | Treble | VINTF files | SELinux files |",
    "|---|---:|---|---:|---:|---:|---|---|---:|---:|",
]
for label,p,vintf,selinux in rows:
    lines.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
        label,
        p.get("ro.build.version.sdk",""),
        p.get("ro.build.version.release",""),
        p.get("ro.product.first_api_level",""),
        p.get("ro.vendor.api_level",""),
        p.get("ro.board.api_level",""),
        p.get("ro.vndk.version",""),
        p.get("ro.treble.enabled",""),
        vintf,
        selinux,
    ))

lines += [
    "",
    "## Guardrails",
    "",
    "- Donor hardware partitions are never copied to joyeuse.",
    "- Target vendor/ODM are treated as hardware-side inputs and audited against Android 16 userspace.",
    "- A missing or conflicting VINTF/HAL declaration is a compatibility issue to patch narrowly, not a reason to disable SELinux globally.",
    "- Filesystem type must be compatible with the selected GXT kernel before any candidate super image is emitted.",
    "",
    "## Raw property deltas",
    "",
]

all_keys=set(keys)
for _,p,_,_ in rows:
    all_keys.update(k for k in p if any(t in k for t in ("api_level","vndk","treble","build.version","abilist")))
for k in sorted(all_keys):
    vals={label:p.get(k,"") for label,p,_,_ in rows}
    if len(set(vals.values())) > 1:
        lines.append(f"### {k}")
        for label,v in vals.items():
            lines.append(f"- {label}: `{v}`")
        lines.append("")

out.write_text("\n".join(lines)+"\n")
print(out.read_text())
