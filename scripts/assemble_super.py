#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
from pathlib import Path

REPLACE_BASES=("system","system_ext","product")

def align(n,a=4096):
    return ((n+a-1)//a)*a

def image_for_partition(name, donor_dir, target_dir):
    base=name[:-2] if name.endswith(("_a","_b")) else name
    slot=name[-2:] if name.endswith(("_a","_b")) else ""
    if base in REPLACE_BASES and slot != "_b":
        p=donor_dir/(base+".img")
        if p.exists():
            return p,"donor"
    p=target_dir/(name+".img")
    if p.exists():
        return p,"target"
    if slot:
        p=target_dir/(base+".img")
        if p.exists() and slot != "_b":
            return p,"target"
    return None,"empty"

def fs_desc(path):
    if not path:
        return ""
    return subprocess.check_output(["file","-b",str(path)],text=True).strip()

ap=argparse.ArgumentParser()
ap.add_argument("layout_json")
ap.add_argument("donor_dir")
ap.add_argument("target_dir")
ap.add_argument("output")
ap.add_argument("--lpmake",default="lpmake")
ap.add_argument("--allow-erofs",action="store_true")
ap.add_argument("--dry-run",action="store_true")
args=ap.parse_args()

layout=json.loads(Path(args.layout_json).read_text())
donor=Path(args.donor_dir)
target=Path(args.target_dir)
output=Path(args.output)

devices=layout["block_devices"]
if len(devices)!=1:
    raise SystemExit(f"refusing multi-device super layout: {len(devices)} block devices")
device=devices[0]
if device["name"]!="super":
    raise SystemExit(f"unexpected super block device name: {device['name']}")

groups={g["name"]:g for g in layout["groups"]}
parts=[]
erofs_donor=[]
for p in layout["partitions"]:
    img,origin=image_for_partition(p["name"],donor,target)
    size=0
    desc=""
    if img:
        size=align(img.stat().st_size)
        desc=fs_desc(img)
        if origin=="donor" and "erofs" in desc.lower():
            erofs_donor.append((p["name"],str(img),desc))
    parts.append({**p,"image":str(img) if img else None,"origin":origin,"size":size,"file":desc})

if erofs_donor and not args.allow_erofs:
    print("EROFS donor image(s) detected while current GXT 4.14.357 port target has no EROFS support:")
    for name,path,desc in erofs_donor:
        print(f"- {name}: {path}: {desc}")
    raise SystemExit(3)

usage={name:0 for name in groups}
for p in parts:
    if p["group"] in usage:
        usage[p["group"]]+=p["size"]
for name,total in usage.items():
    limit=groups[name]["maximum_size"]
    if limit and total>limit:
        raise SystemExit(f"group {name} overflow: images need {total} bytes, max {limit}")

cmd=[
    args.lpmake,
    "--metadata-size",str(layout["metadata_max_size"]),
    "--metadata-slots",str(layout["metadata_slot_count"]),
    "--super-name","super",
    "--device",f"super:{device['size']}",
]
for g in layout["groups"]:
    if g["name"]=="default" and not g["maximum_size"]:
        continue
    cmd += ["--group",f"{g['name']}:{g['maximum_size']}"]

for p in parts:
    attrs="readonly" if "readonly" in (p.get("attributes") or "") else "none"
    cmd += ["--partition",f"{p['name']}:{attrs}:{p['size']}:{p['group']}"]
    if p["image"]:
        cmd += ["--image",f"{p['name']}={p['image']}"]

cmd += ["--sparse","--output",str(output)]

report={
    "device_size":device["size"],
    "metadata_max_size":layout["metadata_max_size"],
    "metadata_slot_count":layout["metadata_slot_count"],
    "group_usage":{k:{"used":usage[k],"max":groups[k]["maximum_size"]} for k in usage},
    "partitions":parts,
    "command":cmd,
}
Path("super-compose-plan.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))

if args.dry_run:
    raise SystemExit(0)

output.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(cmd,check=True)
subprocess.run([args.lpmake.replace("lpmake","lpdump") if args.lpmake.endswith("lpmake") else "lpdump",str(output)],check=False)
print(f"built {output} ({output.stat().st_size} bytes)")
