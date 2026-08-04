#!/usr/bin/env bash
set -euo pipefail

SRC_ZIP="${1:-$HOME/Downloads/lsfg-vk-2.0.0-dev.zip}"
PATCH_FILE="${2:-$HOME/Downloads/lsfg-vk-2.0-dev28-hot1x.patch}"
OUT_DIR="${3:-$HOME/lsfg-vk-hot1x-build}"
PLUGIN_LIB_DEST="$HOME/.local/share/decky-lsfg-vk2-arm64/lib/liblsfg-vk-layer.so"
PLUGIN_MANIFEST_DIR="$HOME/.local/share/decky-lsfg-vk2-arm64/layer"

sudo dnf install -y gcc-c++ cmake ninja-build make patch vulkan-headers vulkan-loader-devel libdrm-devel python3 unzip
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"
unzip -q "$SRC_ZIP" -d "$OUT_DIR"
SRC_DIR=$(find "$OUT_DIR" -maxdepth 1 -type d -name 'lsfg-vk-*' | head -n1)
if [[ -z "$SRC_DIR" ]]; then
  echo "Could not locate source directory after unzip" >&2
  exit 1
fi
patch -d "$SRC_DIR" -p1 < "$PATCH_FILE"
cmake -S "$SRC_DIR" -B "$OUT_DIR/build" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DLSFGVK_BUILD_UI=OFF \
  -DLSFGVK_BUILD_CLI=OFF \
  -DLSFGVK_BUILD_VK_LAYER=ON
cmake --build "$OUT_DIR/build" -j"$(nproc)" --target lsfg-vk-layer
file "$OUT_DIR/build/lsfg-vk-layer/liblsfg-vk-layer.so"
mkdir -p "$(dirname "$PLUGIN_LIB_DEST")" "$PLUGIN_MANIFEST_DIR"
cp -f "$OUT_DIR/build/lsfg-vk-layer/liblsfg-vk-layer.so" "$PLUGIN_LIB_DEST"
if [[ -f "$OUT_DIR/build/lsfg-vk-layer/VkLayer_LSFGVK_frame_generation.json" ]]; then
  cp -f "$OUT_DIR/build/lsfg-vk-layer/VkLayer_LSFGVK_frame_generation.json" "$PLUGIN_MANIFEST_DIR/"
fi
echo
sha256sum "$PLUGIN_LIB_DEST"
echo "Installed patched lib to: $PLUGIN_LIB_DEST"
echo "Now restart the game and test 1X <-> 2X live."
