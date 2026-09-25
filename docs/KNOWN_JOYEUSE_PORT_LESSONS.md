# Known joyeuse/miatoll port lessons

These are verified lessons from the previous Android 15 port work. They are regression checks, not patches to apply blindly to Android 16.

## SELinux / vendor overlays

A previous peaceSU build forced `androidboot.selinux=permissive` in the boot cmdline. When enforcing was enabled, two APKs under `/vendor/overlay` had `vendor_file` xattrs even though platform file contexts expected `vendor_overlay_file`. Zygote/webview_zygote then failed and system_server requested an orderly reboot.

For this project:
- never use global permissive mode as the compatibility solution;
- inspect actual target vendor overlay xattrs and file_contexts;
- fix specific labeling/policy mismatches only when reproduced.

## Embedded video preview corruption

On the previous A15 port, normal playback worked while embedded previews in apps such as Instagram/TikTok corrupted under `debug.hwui.renderer=skiavk`. Switching only HWUI to `skiagl` removed the reproduced corruption.

For this project:
- do not assume Codec2 is at fault if normal playback is healthy;
- test HWUI renderer behavior first if the same symptom appears;
- do not force `skiagl` in the base ROM unless A16 reproduces the bug.

## Rule

Carry evidence forward, not old-port assumptions. Every compatibility patch in the A16 port must have a reproduced symptom and a narrow reason.
