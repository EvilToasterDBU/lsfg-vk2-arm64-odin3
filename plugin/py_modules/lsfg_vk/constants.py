"""Constants for the self-contained lsfg-vk 2 ARM64 plugin."""
from pathlib import Path

INSTALL_BASE = ".local/share/decky-lsfg-vk2-arm64"
LOCAL_LIB = f"{INSTALL_BASE}/lib"
LOCAL_SHARE_BASE = INSTALL_BASE
VULKAN_LAYER_DIR = f"{INSTALL_BASE}/layer"
CONFIG_DIR = ".config/decky-lsfg-vk2-arm64"
SCRIPT_NAME = ".local/bin/lsfg-vk2-arm64"
CONFIG_FILENAME = "conf.toml"
LIB_FILENAME = "liblsfg-vk-layer.so"
JSON_FILENAME = "VkLayer_LSFGVK_frame_generation.json"
CLI_FILENAME = "lsfg-vk-cli2-arm64"

# Kept for modules inherited from the original plugin.
FLATPAK_23_08_FILENAME = "org.freedesktop.Platform.VulkanLayer.lsfg_vk_23.08.flatpak"
FLATPAK_24_08_FILENAME = "org.freedesktop.Platform.VulkanLayer.lsfg_vk_24.08.flatpak"
FLATPAK_25_08_FILENAME = "org.freedesktop.Platform.VulkanLayer.lsfg_vk_25.08.flatpak"
BIN_DIR = "bin"
STEAM_COMMON_PATH = Path("steamapps/common/Lossless Scaling")
LOSSLESS_DLL_NAME = "Lossless.dll"
ENV_LSFG_DLL_PATH = "LSFGVK_DLL_PATH"
ENV_XDG_DATA_HOME = "XDG_DATA_HOME"
ENV_HOME = "HOME"
