# Port status

Last updated: 2026-09-25

## Completed

- Repository and reproducible CI skeleton created.
- Donor pinned to creek Global OS3.0.304.0.WBOMIXM (Android 16).
- Clean joyeuse stock reference pinned to V14.0.3.0.SJZMIXM.
- GXT 4.14.357 non-root and MULTIKSU release inputs pinned and checksum-verified in Actions.
- Donor hardware partitions are explicitly blocked from target packaging.
- SELinux target remains enforcing; ROM-level fingerprint/device spoofing remains disabled.
- Target extraction supports both direct vendor/ODM images and Xiaomi dynamic `super.img`.
- Dynamic-partition tools are pinned to a fixed upstream commit.
- Android image metadata/VINTF collection scripts have been added for compatibility analysis.
- Target dynamic-super extraction now preserves every unpacked partition image, not only vendor/ODM.
- Target LP text is parsed into `target-super-layout.json` for machine-readable compose geometry.
- Super composition now fails closed if a required donor framework image is missing or if any non-empty target partition would otherwise be rebuilt empty.
- Donor and target extraction workflows now collect compact property/VINTF metadata artifacts for the next compatibility pass.

## CI fixes found from real runs

1. `payload-dumper-go` release is tagged `2.1.0`, not `v2.1.0`; module installation by the guessed tag failed.
2. The extractor now checks out the exact 2.1.0 source commit `c3a50ba8d784764c06143c1f82971cd81a77f9d6`.
3. Building that source needs liblzma development headers; `liblzma-dev` is now installed in the donor extraction workflow.
4. Kernel release checksum files contain an `artifacts/` path; kernel verification now verifies the hash against the locally downloaded asset name instead.

## Running / gating work

- Donor userspace extraction: extract only `system`, `system_ext`, and `product`; identify exact filesystem types.
- Target hardware extraction: obtain target `vendor`/ODM from either direct images or `super.img`; record dynamic partition layout.
- No candidate `super.img` will be emitted until both layouts are known and compatible.
- The currently running donor run #36151541280 and target run #36151172182 were started before the full-preservation/VINTF workflow updates. Their manifests/layout remain useful for filesystem and geometry discovery; candidate assembly must use the hardened pipeline.

## Main compatibility gates before first boot candidate

- donor filesystem type vs GXT 4.14.357 filesystem support;
- Android 16 framework/vendor API and VNDK compatibility;
- VINTF/HAL compatibility;
- graphics/gralloc/composer;
- audio, camera, NFC, sensors, Wi-Fi/Bluetooth;
- init/property contexts;
- SELinux labels/policy;
- boot/ramdisk strategy for Android 16 on joyeuse.

## EROFS note

The checked GXT 4.14.357 non-root/KSUN/MULTIKSU branches currently do not contain `fs/erofs`. If the exact creek userspace images are EROFS, the preferred next decision is between a validated kernel EROFS backport and a metadata-preserving filesystem rebuild; the pipeline must not silently convert images.

## Port assembly implementation

- Added `parse_lpdump.py` to turn the target's real LP metadata into machine-readable geometry.
- Added `assemble_super.py` to preserve target-side partitions and replace only `system`, `system_ext`, and `product` from the donor.
- The composer validates dynamic-partition group capacity before running `lpmake`.
- The composer refuses donor EROFS images unless EROFS is explicitly allowed after kernel support is proven.
- Added CI tests for LP metadata parsing and dry-run super composition.
- Added regression coverage proving that a missing non-empty target partition exits with code 5 and a missing donor framework image exits with code 4.
- Validation runs for the preservation, fail-closed, and metadata-collection changes all pass on GitHub-hosted Actions.
