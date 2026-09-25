#!/usr/bin/env bash
set -euo pipefail

IMG=${1:?image path}
LABEL=${2:?label}
OUT=${3:-metadata}
mkdir -p "$OUT/$LABEL"

work=$(mktemp -d)
raw="$IMG"
mounted=0
cleanup() {
  set +e
  if [[ "$mounted" == 1 ]]; then sudo umount "$work/mnt"; fi
  rm -rf "$work"
}
trap cleanup EXIT

desc=$(file -b "$IMG")
printf '%s\n' "$desc" > "$OUT/$LABEL/file.txt"

if grep -qi "Android sparse image" <<<"$desc"; then
  simg2img "$IMG" "$work/raw.img"
  raw="$work/raw.img"
fi

mkdir -p "$work/mnt"
sudo mount -o loop,ro "$raw" "$work/mnt"
mounted=1

{
  for p in     build.prop     system/build.prop     system_ext/build.prop     product/build.prop     vendor/build.prop     odm/build.prop; do
    if [[ -f "$work/mnt/$p" ]]; then
      echo "### $p"
      grep -E '^(ro\.(build|product|vendor|system|system_ext|odm|vndk|treble|board)\.|ro\.sf\.|persist\.sys\.)' "$work/mnt/$p" || true
    fi
  done
} > "$OUT/$LABEL/properties.txt"

find "$work/mnt" -type f \( -path '*/etc/vintf/*' -o -path '*/etc/selinux/*' \) -printf '%P\n' 2>/dev/null | sort > "$OUT/$LABEL/metadata-files.txt"

while IFS= read -r rel; do
  case "$rel" in
    */etc/vintf/*.xml|*/etc/vintf/manifest*.xml|*/etc/vintf/compatibility*.xml)
      dst="$OUT/$LABEL/files/$rel"
      mkdir -p "$(dirname "$dst")"
      cp "$work/mnt/$rel" "$dst"
      ;;
  esac
done < "$OUT/$LABEL/metadata-files.txt"

find "$work/mnt" -maxdepth 3 -type d -printf '%P\n' 2>/dev/null | sort > "$OUT/$LABEL/top-dirs.txt"
sudo umount "$work/mnt"
mounted=0

echo "collected metadata for $LABEL from $IMG"
