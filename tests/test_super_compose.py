#!/usr/bin/env python3
import json
import subprocess
import tempfile
from pathlib import Path

root=Path(__file__).resolve().parents[1]

def run_compose(layout, donor, target, cwd, expect=0):
    layout_path=cwd/"layout.json"
    layout_path.write_text(json.dumps(layout))
    p=subprocess.run([
        "python3",str(root/"scripts/assemble_super.py"),str(layout_path),str(donor),str(target),
        str(cwd/"super.img"),"--dry-run"
    ],cwd=cwd)
    assert p.returncode==expect,(p.returncode,expect)

with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    donor=td/"donor"; target=td/"target"
    donor.mkdir(); target.mkdir()
    for name,size in (("system.img",8192),("system_ext.img",4096),("product.img",4096)):
        (donor/name).write_bytes(b"X"*size)
    (target/"vendor.img").write_bytes(b"V"*8192)

    layout={
        "metadata_version":"10.0",
        "metadata_max_size":65536,
        "metadata_slot_count":2,
        "block_devices":[{"name":"super","first_sector":2048,"size":64*1024*1024,"flags":"none"}],
        "groups":[
            {"name":"default","maximum_size":0,"flags":"none"},
            {"name":"qti_dynamic_partitions","maximum_size":48*1024*1024,"flags":"none"}
        ],
        "partitions":[
            {"name":"system","group":"qti_dynamic_partitions","attributes":"readonly","extent_bytes":16*1024*1024},
            {"name":"system_ext","group":"qti_dynamic_partitions","attributes":"readonly","extent_bytes":8*1024*1024},
            {"name":"product","group":"qti_dynamic_partitions","attributes":"readonly","extent_bytes":8*1024*1024},
            {"name":"vendor","group":"qti_dynamic_partitions","attributes":"readonly","extent_bytes":16*1024*1024}
        ]
    }
    run_compose(layout,donor,target,td)
    plan=json.loads((td/"super-compose-plan.json").read_text())
    origins={p["name"]:p["origin"] for p in plan["partitions"]}
    assert origins=={"system":"donor","system_ext":"donor","product":"donor","vendor":"target"},origins
    assert plan["device_size"]==64*1024*1024
    assert plan["group_usage"]["qti_dynamic_partitions"]["used"]>0

    # A non-empty preserved target partition may never be silently rebuilt as
    # zero bytes.
    bad=json.loads(json.dumps(layout))
    bad["partitions"].append({
        "name":"mi_ext",
        "group":"qti_dynamic_partitions",
        "attributes":"readonly",
        "extent_bytes":4096,
    })
    run_compose(bad,donor,target,td,expect=5)

    # A framework partition must come from the donor. Falling back to the
    # target framework is not a valid port.
    (donor/"system_ext.img").unlink()
    run_compose(layout,donor,target,td,expect=4)

sample="""Metadata version: 10.0
Metadata size: 592 bytes
Metadata max size: 65536 bytes
Metadata slot count: 2
Partition table:
------------------------
Name: system
Group: qti_dynamic_partitions
Attributes: readonly
Extents:
0 .. 2047 linear super 2048
------------------------
Name: vendor
Group: qti_dynamic_partitions
Attributes: readonly
Extents:
0 .. 1023 linear super 4096
------------------------
Block device table:
------------------------
Partition name: super
First sector: 2048
Size: 8589934592 bytes
Flags: none
------------------------
Group table:
------------------------
Name: default
Maximum size: 0 bytes
Flags: none
------------------------
Name: qti_dynamic_partitions
Maximum size: 8585740288 bytes
Flags: none
------------------------
"""
with tempfile.TemporaryDirectory() as td2:
    td2=Path(td2)
    (td2/"dump.txt").write_text(sample)
    subprocess.run(["python3",str(root/"scripts/parse_lpdump.py"),str(td2/"dump.txt"),str(td2/"layout.json")],check=True)
    parsed=json.loads((td2/"layout.json").read_text())
    assert parsed["metadata_max_size"]==65536
    assert parsed["metadata_slot_count"]==2
    assert parsed["block_devices"][0]["size"]==8589934592
    assert parsed["partitions"][0]["extent_bytes"]==2048*512
    assert parsed["groups"][1]["maximum_size"]==8585740288

print("super compose/parser tests OK")
