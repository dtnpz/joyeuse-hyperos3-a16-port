# GXT HyperOS 3 Android 16 port for joyeuse

Experimental clean-room port workspace for Redmi Note 9 Pro (joyeuse / miatoll).

## Current target

- Target: Redmi Note 9 Pro (joyeuse)
- Donor userspace: Redmi 15 / POCO M7 4G (creek)
- Donor build: OS3.0.304.0.WBOMIXM
- Android: 16
- Clean target hardware reference: joyeuse Global V14.0.3.0.SJZMIXM (Android 12)
- Kernel target: GXT 4.14.357
- SELinux goal: enforcing
- ROM-level device/fingerprint spoofing: disabled by design

The donor userspace and joyeuse hardware stack are treated separately. Never flash creek boot, init_boot, vendor_boot, DTBO, vendor, ODM, modem, firmware or other board-specific images to joyeuse.

The pinned Android 12 Xiaomi fastboot ROM is a reproducible clean hardware/vendor reference, **not** a claim that its vendor stack is already Android 16 compatible. Compatibility must be demonstrated and patched narrowly.

## CI / Actions

- `validate.yml`: validates pinned donor/target configuration on every change.
- `donor-smoke.yml`: downloads the pinned creek OTA, verifies MD5 and OTA structure, and emits a small manifest.
- `target-stock-smoke.yml`: verifies the pinned official joyeuse fastboot baseline and emits a small manifest.
- `extract-donor.yml`: selectively extracts `system`, `system_ext` and `product` from the donor OTA and identifies their filesystem types.
- `extract-target.yml`: selectively extracts target-side hardware reference images without expanding the entire fastboot package.

Large source ROMs and extracted images are not committed to Git.

## Guardrails

- joyeuse-only first; miatoll-unified comes later.
- No global permissive SELinux workaround.
- No ROM-level device/fingerprint spoofing.
- No creek firmware/modem/boot-chain images in the target package.
- GXT 4.14.357 currently has no `fs/erofs` on the checked non-KSU/KSUN/MULTIKSU branches, so an EROFS donor image cannot simply be flashed as-is.
- Root variants are integrated only after a reproducible non-root boot baseline exists.

See `docs/PORT_PLAN.md`, `docs/KERNEL_FILESYSTEM_NOTE.md`, and `docs/KNOWN_JOYEUSE_PORT_LESSONS.md`.
