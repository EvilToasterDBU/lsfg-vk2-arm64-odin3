"""Self-contained installer for the patched lsfg-vk 2 ARM64 Hot-1X layer."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import traceback
from pathlib import Path
from typing import Iterable

from .base_service import BaseService
from .constants import CLI_FILENAME, JSON_FILENAME, LIB_FILENAME
from .config_schema import ConfigurationManager
from .types import InstallationCheckResponse, InstallationResponse, UninstallationResponse


class InstallationService(BaseService):
    """Install the bundled AArch64 layer without downloads or system changes."""

    EXPECTED_MACHINE = 183  # EM_AARCH64

    def __init__(self, logger=None):
        super().__init__(logger)
        self.lib_file = self.local_lib_dir / LIB_FILENAME
        self.json_file = self.local_share_dir / JSON_FILENAME
        self.cli_file = self.user_home / ".local/bin" / CLI_FILENAME

        self.plugin_root = Path(__file__).resolve().parents[2]
        self.bundle_dir = self.plugin_root / "bin" / "arm64-hot1x"
        self.bundled_lib = self.bundle_dir / LIB_FILENAME
        self.bundled_manifest = self.bundle_dir / JSON_FILENAME

    def install(self) -> InstallationResponse:
        """Install or repair the bundled Hot-1X engine while preserving config."""
        try:
            if not self._is_arm_architecture():
                raise RuntimeError(
                    "This build requires an AArch64 Armada host. "
                    f"Detected process architecture: {platform.machine()}"
                )

            self._validate_bundle()
            self._ensure_directories()
            self.lsfg_launch_script_path.parent.mkdir(parents=True, exist_ok=True)

            self._install_binary(self.bundled_lib, self.lib_file, 0o755)
            self._install_manifest(self.bundled_manifest)
            self._create_config_file()
            self._create_lsfg_launch_script()
            self._fix_owner_and_modes()

            status = self.check_installation()
            if not status.get("installed"):
                raise RuntimeError(status.get("error") or "Installation verification failed")

            return self._success_response(
                InstallationResponse,
                "Patched lsfg-vk 2 ARM64 Hot-1X installed successfully",
            )
        except Exception as exc:
            self.log.error("Error installing bundled lsfg-vk 2 ARM64: %s", exc)
            self.log.debug(traceback.format_exc())
            return self._error_response(InstallationResponse, str(exc), message="")

    def _is_arm_architecture(self) -> bool:
        if platform.machine().lower() in {"aarch64", "arm64", "x86_64"}:
            return True
        # Decky's backend may run through FEX, while the host itself is native ARM64.
        if Path("/usr/libexec/armada/device-env").is_file():
            self.log.info("Detected native AArch64 Armada host through device-env")
            return True
        if Path("/usr/lib/pocknix/device.conf").is_file():
            self.log.info("Detected native AArch64 Armada host through device-env")
            return True
        try:
            with Path("/proc/1/exe").open("rb") as fh:
                header = fh.read(20)
            if header[:4] == b"\x7fELF" and len(header) >= 20:
                order = "little" if header[5] == 1 else "big"
                return int.from_bytes(header[18:20], order) == self.EXPECTED_MACHINE
        except OSError:
            pass
        return False

    def _validate_bundle(self) -> None:
        if not self.bundled_lib.is_file():
            raise RuntimeError(f"Bundled layer is missing: {self.bundled_lib}")
        if not self.bundled_manifest.is_file():
            raise RuntimeError(f"Bundled manifest is missing: {self.bundled_manifest}")
        self._verify_elf(self.bundled_lib, self.EXPECTED_MACHINE)
        data = json.loads(self.bundled_manifest.read_text(encoding="utf-8"))
        layer = data.get("layer") or {}
        if layer.get("name") != "VK_LAYER_LSFGVK_frame_generation":
            raise RuntimeError("Bundled Vulkan manifest has an unexpected layer name")

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _install_binary(self, source: Path, destination: Path, mode: int) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(f".{destination.name}.installing")
        try:
            with source.open("rb") as src, temporary.open("wb") as dst:
                shutil.copyfileobj(src, dst, length=1024 * 1024)
                dst.flush()
                os.fsync(dst.fileno())
            temporary.chmod(mode)
            os.replace(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)
        self.log.info("Installed bundled file: %s", destination)

    def _install_manifest(self, source: Path) -> None:
        data = json.loads(source.read_text(encoding="utf-8"))
        layer = data.setdefault("layer", {})
        layer["name"] = "VK_LAYER_LSFGVK_frame_generation"
        layer["library_path"] = str(self.lib_file)
        layer["disable_environment"] = {"DISABLE_LSFGVK": "1"}
        self._write_file(self.json_file, json.dumps(data, indent=2) + "\n", 0o644)

    @staticmethod
    def _verify_elf(path: Path, expected_machine: int) -> None:
        with path.open("rb") as fh:
            header = fh.read(20)
        if len(header) < 20 or header[:4] != b"\x7fELF":
            raise RuntimeError(f"File is not an ELF binary: {path}")
        byte_order = "little" if header[5] == 1 else "big"
        machine = int.from_bytes(header[18:20], byte_order)
        if machine != expected_machine:
            names = {62: "x86-64", 183: "AArch64"}
            raise RuntimeError(
                f"Wrong architecture for {path.name}: expected {names.get(expected_machine)}, "
                f"got {names.get(machine, machine)}"
            )

    def _create_config_file(self) -> None:
        from .dll_detection import DllDetectionService

        dll_service = DllDetectionService(self.log)
        if self.config_file_path.exists():
            try:
                profile_data = ConfigurationManager.parse_toml_content_multi_profile(
                    self.config_file_path.read_text(encoding="utf-8")
                )
                detected = dll_service.check_lossless_scaling_dll()
                if detected.get("detected") and detected.get("path"):
                    profile_data["global_config"]["dll"] = detected["path"]
                content = ConfigurationManager.generate_toml_content_multi_profile(profile_data)
            except Exception as exc:
                self.log.warning("Could not preserve existing config; creating a clean one: %s", exc)
                config = ConfigurationManager.get_defaults_with_dll_detection(dll_service)
                content = ConfigurationManager.generate_toml_content(config)
        else:
            config = ConfigurationManager.get_defaults_with_dll_detection(dll_service)
            content = ConfigurationManager.generate_toml_content(config)
        self._write_file(self.config_file_path, content, 0o644)

    def _create_lsfg_launch_script(self) -> None:
        from .configuration import ConfigurationService

        service = ConfigurationService(logger=self.log)
        service.user_home = self.user_home
        service.lsfg_script_path = self.lsfg_launch_script_path
        service.lsfg_launch_script_path = self.lsfg_launch_script_path
        try:
            profile_data = service._get_profile_data()
            content = service._generate_script_content_for_profile(profile_data)
        except Exception as exc:
            self.log.warning("Could not read profile while creating wrapper: %s", exc)
            content = service._generate_script_content(ConfigurationManager.get_defaults())
        self._write_file(self.lsfg_launch_script_path, content, 0o755)

    def _fix_owner_and_modes(self) -> None:
        try:
            st = self.user_home.stat()
            targets: Iterable[Path] = (
                self.local_lib_dir,
                self.local_share_dir,
                self.config_dir,
                self.lsfg_launch_script_path,
            )
            for target in targets:
                if not target.exists():
                    continue
                if target.is_dir():
                    for root, dirs, files in os.walk(target):
                        os.chown(root, st.st_uid, st.st_gid)
                        for name in dirs + files:
                            try:
                                os.chown(os.path.join(root, name), st.st_uid, st.st_gid)
                            except OSError:
                                pass
                else:
                    os.chown(target, st.st_uid, st.st_gid)
        except OSError as exc:
            self.log.warning("Could not normalize ownership: %s", exc)

    def check_installation(self) -> InstallationCheckResponse:
        try:
            self._validate_bundle()
            lib_exists = self.lib_file.is_file()
            json_exists = self.json_file.is_file()
            script_exists = self.lsfg_launch_script_path.is_file()
            valid_arch = False
            bundle_matches = False
            manifest_valid = False
            wrapper_valid = False
            errors: list[str] = []

            if lib_exists:
                try:
                    self._verify_elf(self.lib_file, self.EXPECTED_MACHINE)
                    valid_arch = True
                    bundle_matches = self._sha256(self.lib_file) == self._sha256(self.bundled_lib)
                    if not bundle_matches:
                        errors.append("Installed layer does not match the bundled Hot-1X build")
                except Exception as exc:
                    errors.append(str(exc))

            if json_exists:
                try:
                    data = json.loads(self.json_file.read_text(encoding="utf-8"))
                    layer = data.get("layer") or {}
                    manifest_valid = (
                        layer.get("name") == "VK_LAYER_LSFGVK_frame_generation"
                        and Path(str(layer.get("library_path", ""))) == self.lib_file
                    )
                    if not manifest_valid:
                        errors.append("Installed Vulkan manifest is invalid")
                except Exception as exc:
                    errors.append(f"Manifest parse failed: {exc}")

            if script_exists:
                content = self.lsfg_launch_script_path.read_text(encoding="utf-8", errors="replace")
                wrapper_valid = (
                    "VK_IMPLICIT_LAYER_PATH" in content
                    and "ENABLE_GAMESCOPE_WSI=0" in content
                    and "unset DISABLE_LSFGVK" in content
                )
                if not wrapper_valid:
                    errors.append("Launch wrapper is not the Hot-1X Armada wrapper")

            installed = all((
                lib_exists,
                json_exists,
                script_exists,
                valid_arch,
                bundle_matches,
                manifest_valid,
                wrapper_valid,
            ))

            return {
                "installed": installed,
                "lib_exists": lib_exists and valid_arch and bundle_matches,
                "json_exists": json_exists and manifest_valid,
                "script_exists": script_exists and wrapper_valid,
                "lib_path": str(self.lib_file),
                "json_path": str(self.json_file),
                "script_path": str(self.lsfg_launch_script_path),
                "error": "; ".join(errors) if errors else None,
                "bundled": True,
                "bundle_matches": bundle_matches,
            }
        except Exception as exc:
            return {
                "installed": False,
                "lib_exists": False,
                "json_exists": False,
                "script_exists": False,
                "lib_path": str(self.lib_file),
                "json_path": str(self.json_file),
                "script_path": str(self.lsfg_launch_script_path),
                "error": str(exc),
                "bundled": True,
                "bundle_matches": False,
            }

    def uninstall(self) -> UninstallationResponse:
        try:
            removed = []
            for path in (self.lib_file, self.json_file, self.cli_file, self.lsfg_launch_script_path):
                if self._remove_if_exists(path):
                    removed.append(str(path))
            install_root = self.user_home / ".local/share/decky-lsfg-vk2-arm64"
            if install_root.exists():
                shutil.rmtree(install_root)
                removed.append(str(install_root))
            # User configuration is intentionally preserved across plugin reinstallations.
            return self._success_response(
                UninstallationResponse,
                f"Removed {len(removed)} lsfg-vk 2 ARM64 files/directories",
                removed_files=removed or None,
            )
        except Exception as exc:
            return self._error_response(
                UninstallationResponse, str(exc), message="", removed_files=None
            )

    def cleanup_on_uninstall(self):
        """Decky lifecycle compatibility wrapper."""
        return self.uninstall()
