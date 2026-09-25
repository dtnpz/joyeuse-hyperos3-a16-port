#!/usr/bin/env bash
set -euo pipefail

IN=${1:-target-out}
OUT=${2:-target-hardware}
TOOLS=${3:-tools/lp}
mkdir -p "$OUT"

copy_if_present() {
  local n=$1
  if [[ -f "$IN/$n" ]]; then
    cp --reflink=auto "$IN/$n" "$OUT/$n"
  fi
}

copy_if_present boot.img
copy_if_present dtbo.img

if [[ -f "$IN/vendor.img" ]]; then
  for img in "$IN"/*.img; do
    [[ -e "$img" ]] || continue
    cp --reflink=auto "$img" "$OUT/$(basename "$img")"
  done
  echo "target hardware layout: direct partition images"
  exit 0
fi

[[ -f "$IN/super.img" ]] || { echo "missing super.img/vendor.img" >&2; exit 1; }
command -v simg2img >/dev/null
[[ -x "$TOOLS/lpunpack" ]] || { echo "missing $TOOLS/lpunpack" >&2; exit 1; }
[[ -x "$TOOLS/lpdump" ]] || { echo "missing $TOOLS/lpdump" >&2; exit 1; }

SUPER="$IN/super.img"
RAW="$IN/super.raw.img"
if file -b "$SUPER" | grep -qi "Android sparse image"; then
  simg2img "$SUPER" "$RAW"
  rm -f "$SUPER"
else
  mv "$SUPER" "$RAW"
fi

"$TOOLS/lpdump" "$RAW" > target-super-layout.txt
python3 scripts/parse_lpdump.py target-super-layout.txt target-super-layout.json

mkdir -p "$IN/lp"
"$TOOLS/lpunpack" "$RAW" "$IN/lp"
rm -f "$RAW"

# Preserve every target dynamic-partition image. assemble_super.py replaces only
# system/system_ext/product with donor images and keeps all remaining target
# partitions (mi_ext, vendor/odm, *_dlkm, etc.) byte-for-byte.
for img in "$IN"/lp/*.img; do
  [[ -e "$img" ]] || continue
  mv "$img" "$OUT/$(basename "$img")"
done

if [[ ! -f "$OUT/vendor.img" && ! -f "$OUT/vendor_a.img" ]]; then
  echo "super unpack did not produce vendor(.img|_a.img)" >&2
  exit 1
fi

echo "target hardware layout: dynamic super -> preserved all dynamic partition images"
