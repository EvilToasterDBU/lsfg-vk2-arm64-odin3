# v0.13.0 — Odin 3 ARM64 Hot 1X

Initial public device-specific release.

## Included

- Native AArch64 `liblsfg-vk-layer.so` built on AYN Odin 3 / Fedora 44.
- Self-contained installation with no runtime download or compilation.
- Live `1X ↔ 2X/3X/4X` switching.
- 1X passthrough keeps the Vulkan layer loaded.
- Private Vulkan implicit-layer path for Armada.
- Gamescope WSI bypass used by the validated Odin 3 configuration.
- Short plugin name: **LSFG-VK 2 ARM64**.
- Multi-path clipboard handling for the launch-option copy button.
- Preserves the existing configuration during reinstall.

## Launch option

```bash
/usr/libexec/armada/armada-game-launch ~/.local/bin/lsfg-vk2-arm64 %command%
```

## Target

AYN Odin 3 running Armada/Fedora ARM64. Other ARM64 devices are not yet validated.
