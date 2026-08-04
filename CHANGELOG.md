# Changelog

## 0.13.0-odin3-arm64.8

- Added native hot 1X passthrough to the lsfg-vk 2.0 development layer.
- Kept the Vulkan layer loaded at 1X so multiplier changes can hot-reload.
- Reserved swapchain image headroom for live switching up to 4X.
- Bundled the validated AArch64 Vulkan layer directly in the Decky plugin.
- Fixed backend installation detection for the private Odin 3 paths.
- Fixed the Python configuration parser indentation regression.
- Added layered clipboard fallbacks for copying the Armada launch option.
- Renamed the visible plugin to `LSFG-VK 2 ARM64`.
