# LSFG-VK 2 ARM64

Self-contained Decky plugin for AYN Odin 3 running Armada. It bundles the tested patched AArch64 `lsfg-vk 2.0.0-dev28` Vulkan layer.

## Features

- Live native `1X` passthrough.
- Hot switching between `1X`, `2X`, `3X`, and `4X` while the game is running.
- No COPR download, `dnf`, `bootc usr-overlay`, or local compilation.
- Automatic engine installation/repair after installing the Decky ZIP.
- Reinstall preserves the existing configuration and profiles.
- Correct Armada/Gamescope launch wrapper.

## Installation

Install the ZIP through Decky Loader developer settings. The bundled engine is deployed automatically when the plugin loads. The Install/Reinstall button also uses the same bundled patched engine and does not access the network.

## Launch option

```bash
/usr/libexec/armada/armada-game-launch ~/.local/bin/lsfg-vk2-arm64 %command%
```

## Files

- `~/.local/share/decky-lsfg-vk2-arm64/lib/liblsfg-vk-layer.so`
- `~/.local/share/decky-lsfg-vk2-arm64/layer/VkLayer_LSFGVK_frame_generation.json`
- `~/.config/decky-lsfg-vk2-arm64/conf.toml`
- `~/.local/bin/lsfg-vk2-arm64`

This is an unofficial community adaptation. Lossless Scaling itself is required for `Lossless.dll`.
