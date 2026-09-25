# Port plan

## Phase 0 — reproducibility

Pin one exact creek Global HyperOS 3 Android 16 recovery package and verify it byte-for-byte in GitHub Actions.

## Phase 1 — donor extraction

Extract only userspace partitions needed from the OTA payload. Do not carry creek boot/vendor/firmware images into the target package.

Candidate donor partitions:
- system
- system_ext
- product

Any mi_ext handling must be reviewed after inspecting the actual payload layout.

## Phase 2 — target baseline

Pin a known-booting joyeuse target package/vendor stack. Record hashes before changing anything.

Keep target-side:
- vendor / ODM
- modem / firmware
- NFC
- camera
- audio
- sensors
- Wi-Fi / Bluetooth
- DTB / DTBO

A full build remains blocked until this input is explicit.

## Phase 3 — Android 16 compatibility

Audit, patch and test in isolated groups:
1. VNDK/linker namespaces and vendor API assumptions
2. graphics/gralloc/composer
3. audio
4. camera provider
5. NFC
6. Wi-Fi/Bluetooth
7. sensors/power/health
8. keystore/keymint/gatekeeper
9. init/property contexts
10. SELinux policy

Do not solve compatibility by globally disabling SELinux.

## Phase 4 — kernel integration

Integrate GXT 4.14.357 only after the userspace/target baseline is reproducible. Keep root variants separable from the non-root boot baseline so a boot failure is attributable.

## Phase 5 — packaging and device test

Produce a joyeuse-only package first. miatoll-unified support comes after joyeuse reaches repeatable boot and core hardware validation.

Required device checks before calling a build usable:
- boot completes
- encryption/data mount
- display/touch
- cellular/data/IMS where supported
- Wi-Fi/Bluetooth
- NFC
- camera
- audio/mic
- sensors
- fingerprint
- charging/USB
- SELinux enforcing
