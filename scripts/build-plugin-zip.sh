#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_DIR="$ROOT/plugin"
OUT_DIR="$ROOT/releases"
NAME="LSFG-VK-2-ARM64-Hot1X-Odin3-v0.13.0.zip"

mkdir -p "$OUT_DIR"
rm -f "$OUT_DIR/$NAME" "$OUT_DIR/$NAME.sha256"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/decky-lsfg-vk2-arm64"
cp -a "$PLUGIN_DIR/." "$TMP/decky-lsfg-vk2-arm64/"
find "$TMP" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$TMP" -type f -name '*.pyc' -delete

(
  cd "$TMP"
  zip -qr "$OUT_DIR/$NAME" decky-lsfg-vk2-arm64
)
sha256sum "$OUT_DIR/$NAME" > "$OUT_DIR/$NAME.sha256"

echo "Built: $OUT_DIR/$NAME"
cat "$OUT_DIR/$NAME.sha256"
