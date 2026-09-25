#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

if len(sys.argv) not in (2,3):
    raise SystemExit("usage: parse_lpdump.py LPDUMP_TXT [OUT_JSON]")

src=Path(sys.argv[1]).read_text(errors="replace").splitlines()
out_path=Path(sys.argv[2]) if len(sys.argv)==3 else Path("super-layout.json")

meta={"metadata_version":None,"metadata_max_size":None,"metadata_slot_count":None}
partitions=[]
groups=[]
devices=[]
section=None
current=None
extent_sectors=0

def flush():
    global current, extent_sectors
    if not current:
        return
    if section=="partition":
        current["extent_sectors"]=extent_sectors
        current["extent_bytes"]=extent_sectors*512
        partitions.append(current)
    elif section=="group":
        groups.append(current)
    elif section=="device":
        devices.append(current)
    current=None
    extent_sectors=0

for raw in src:
    line=raw.strip()
    m=re.match(r"Metadata version:\s*(\S+)",line)
    if m: meta["metadata_version"]=m.group(1); continue
    m=re.match(r"Metadata max size:\s*(\d+) bytes",line)
    if m: meta["metadata_max_size"]=int(m.group(1)); continue
    m=re.match(r"Metadata slot count:\s*(\d+)",line)
    if m: meta["metadata_slot_count"]=int(m.group(1)); continue

    if line=="Partition table:":
        flush(); section="partition"; continue
    if line=="Block device table:":
        flush(); section="device"; continue
    if line=="Group table:":
        flush(); section="group"; continue
    if line=="Super partition layout:":
        flush(); section="layout"; continue
    if line=="------------------------":
        flush(); continue

    if section=="partition":
        m=re.match(r"Name:\s*(\S+)",line)
        if m:
            flush(); current={"name":m.group(1),"group":None,"attributes":None}; continue
        if current:
            m=re.match(r"Group:\s*(\S+)",line)
            if m: current["group"]=m.group(1); continue
            m=re.match(r"Attributes:\s*(.*)",line)
            if m: current["attributes"]=m.group(1).strip(); continue
            m=re.match(r"(\d+) \.\. (\d+) (?:linear|zero)\b",line)
            if m:
                extent_sectors += int(m.group(2))-int(m.group(1))+1
                continue

    if section=="device":
        m=re.match(r"Partition name:\s*(\S+)",line)
        if m:
            flush(); current={"name":m.group(1),"first_sector":None,"size":None,"flags":None}; continue
        if current:
            m=re.match(r"First sector:\s*(\d+)",line)
            if m: current["first_sector"]=int(m.group(1)); continue
            m=re.match(r"Size:\s*(\d+) bytes",line)
            if m: current["size"]=int(m.group(1)); continue
            m=re.match(r"Flags:\s*(.*)",line)
            if m: current["flags"]=m.group(1).strip(); continue

    if section=="group":
        m=re.match(r"Name:\s*(\S+)",line)
        if m:
            flush(); current={"name":m.group(1),"maximum_size":None,"flags":None}; continue
        if current:
            m=re.match(r"Maximum size:\s*(\d+) bytes",line)
            if m: current["maximum_size"]=int(m.group(1)); continue
            m=re.match(r"Flags:\s*(.*)",line)
            if m: current["flags"]=m.group(1).strip(); continue

flush()

if not devices:
    raise SystemExit("no block devices parsed from lpdump output")
if not groups:
    raise SystemExit("no groups parsed from lpdump output")
if not partitions:
    raise SystemExit("no partitions parsed from lpdump output")
if not meta["metadata_max_size"] or not meta["metadata_slot_count"]:
    raise SystemExit("incomplete metadata geometry")

doc={**meta,"block_devices":devices,"groups":groups,"partitions":partitions}
out_path.write_text(json.dumps(doc,indent=2)+"\n")
print(json.dumps(doc,indent=2))
