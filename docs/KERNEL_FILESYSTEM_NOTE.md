# Kernel filesystem constraint

Checked against the current GXT 4.14.357 branches:

- gxterkernl-joyeuse-4.14.357-rev187
- gxterkernl-joyeuse-4.14.357-rev187-ksun
- gxterkernl-joyeuse-4.14.357-rev187-multiksu

None of those branches currently contains `fs/erofs`.

Implication for this port:

1. Inspect the filesystem type of every extracted donor dynamic partition.
2. If a donor partition is EROFS, do not place it directly in the joyeuse package while using these kernel branches.
3. Either rebuild the partition as a filesystem the target kernel supports (expected path: ext4, after preserving Android metadata/xattrs) or separately add and validate an EROFS backport in the kernel.
4. Filesystem conversion must preserve SELinux xattrs, fs_config ownership/modes/capabilities, symlinks and sparse/dynamic-partition sizing.

This is a build-time guardrail, not a claim that every creek partition is EROFS. The donor extraction stage must detect the actual image format.
