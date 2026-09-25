# GXT HyperOS 3 Android 16 port for joyeuse

Experimental clean-room port workspace for Redmi Note 9 Pro (joyeuse / miatoll).

## Current target

- Target: Redmi Note 9 Pro (joyeuse)
- Donor: Redmi 15 / POCO M7 4G (creek)
- Donor build: OS3.0.304.0.WBOMIXM
- Android: 16
- Kernel target: GXT 4.14.357
- SELinux goal: enforcing
- ROM-level device/fingerprint spoofing: disabled by design

The donor userspace and the joyeuse hardware stack are treated separately. Do not flash donor firmware, modem, DTBO, vendor_boot, boot, or other board-specific images from creek onto joyeuse.

## CI

- `validate.yml`: validates pinned donor/target configuration on every change.
- `donor-smoke.yml`: manually or on a `build/**` branch downloads the pinned Xiaomi recovery package, verifies MD5, inspects OTA metadata, and uploads only a small manifest artifact.

A full flashable port is intentionally not emitted until target-side vendor/HAL inputs are pinned and compatibility patches are reviewed.
