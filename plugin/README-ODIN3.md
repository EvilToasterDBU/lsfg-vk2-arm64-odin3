# LSFG-VK 2 ARM64 — Odin 3 / Armada

Self-contained Decky plugin for the patched `lsfg-vk 2.0.0-dev28` AArch64 layer.

## Included

- Ready-to-use patched AArch64 Vulkan layer; no download or compilation.
- Live `1X` passthrough with hot switching to `2X`, `3X`, or `4X`.
- Working Armada/Gamescope isolation path.
- Automatic installation and repair of the bundled engine.
- Existing profiles and `conf.toml` are preserved during reinstall.

## Installed paths

- Layer: `~/.local/share/decky-lsfg-vk2-arm64/lib/liblsfg-vk-layer.so`
- Manifest: `~/.local/share/decky-lsfg-vk2-arm64/layer/VkLayer_LSFGVK_frame_generation.json`
- Config: `~/.config/decky-lsfg-vk2-arm64/conf.toml`
- Wrapper: `~/.local/bin/lsfg-vk2-arm64`

## Armada launch option

```bash
/usr/libexec/armada/armada-game-launch ~/.local/bin/lsfg-vk2-arm64 %command%
```

Use only this LSFG wrapper for the game. Do not combine it with the old `~/lsfg` wrapper.
