#!/usr/bin/env python3
import json
from pathlib import Path
from urllib.parse import urlparse

root = Path(__file__).resolve().parents[1]
donor = json.loads((root / "config/donor.json").read_text())
target = json.loads((root / "config/target.json").read_text())
target_stock = json.loads((root / "config/target-stock.json").read_text())

errors = []

def need(obj, key, scope):
    if key not in obj or obj[key] in ("", None, []):
        errors.append(f"{scope}: missing required field: {key}")

for key in ("codename", "hyperos", "android", "filename", "url", "md5", "use_partitions", "never_flash_to_target"):
    need(donor, key, "donor")
for key in ("codename", "family", "soc", "ram_gb", "kernel_target", "selinux_goal", "hardware_from_target"):
    need(target, key, "target")
for key in ("codename", "miui", "android", "filename", "url", "md5", "role", "candidate_extract"):
    need(target_stock, key, "target-stock")

if donor.get("codename") != "creek":
    errors.append("donor codename must currently be creek")
if donor.get("android") != 16:
    errors.append("donor Android version must be 16")
if target.get("codename") != "joyeuse":
    errors.append("target codename must be joyeuse")
if target.get("family") != "miatoll":
    errors.append("target family must be miatoll")
if target.get("rom_level_spoofing") is not False:
    errors.append("ROM-level spoofing must remain disabled")
if target.get("selinux_goal") != "enforcing":
    errors.append("SELinux goal must remain enforcing")
if target_stock.get("codename") != "joyeuse":
    errors.append("target-stock codename must be joyeuse")
if target_stock.get("android") != 12:
    errors.append("target-stock Android version must be 12 for the pinned Xiaomi baseline")

def check_package(scope, cfg):
    md5 = cfg.get("md5", "")
    if len(md5) != 32:
        errors.append(f"{scope}: md5 must be 32 hex characters")
    else:
        try:
            int(md5, 16)
        except ValueError:
            errors.append(f"{scope}: md5 is not hexadecimal")
    u = urlparse(cfg.get("url", ""))
    if u.scheme != "https" or not u.netloc.endswith("miui.com"):
        errors.append(f"{scope}: URL must be HTTPS on a Xiaomi miui.com host")
    if Path(u.path).name != cfg.get("filename"):
        errors.append(f"{scope}: filename does not match URL")

check_package("donor", donor)
check_package("target-stock", target_stock)

for dangerous in ("vendor", "odm", "modem", "firmware", "dtbo", "vendor_boot", "boot"):
    if dangerous in donor.get("use_partitions", []):
        errors.append(f"unsafe donor partition selected for target: {dangerous}")

if "vendor.img" not in target_stock.get("candidate_extract", []):
    errors.append("target-stock must retain vendor.img as a candidate hardware baseline")

if errors:
    print("CONFIG INVALID")
    for e in errors:
        print(f"- {e}")
    raise SystemExit(1)

print("CONFIG OK")
print(f"donor={donor['codename']} {donor['hyperos']} Android {donor['android']}")
print(f"target={target['codename']} kernel={target['kernel_target']} SELinux={target['selinux_goal']}")
print(f"target-stock={target_stock['miui']} Android {target_stock['android']} ({target_stock['role']})")
