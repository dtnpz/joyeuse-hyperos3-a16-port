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
  copy_if_present vendor.img
  copy_if_present odm.img
  echo "target hardware layout: direct vendor/odm images"
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
mkdir -p "$IN/lp"
"$TOOLS/lpunpack" "$RAW" "$IN/lp"
rm -f "$RAW"

for n in vendor.img odm.img; do
  if [[ -f "$IN/lp/$n" ]]; then
    mv "$IN/lp/$n" "$OUT/$n"
  fi
done

[[ -f "$OUT/vendor.img" ]] || { echo "super unpack did not produce vendor.img" >&2; exit 1; }
echo "target hardware layout: dynamic super -> vendor/odm"
