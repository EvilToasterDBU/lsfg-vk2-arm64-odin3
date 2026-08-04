#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="${1:-lsfg-vk2-arm64-odin3}"
VISIBILITY="${2:-public}"
VERSION="v0.13.0"
ASSET="releases/LSFG-VK-2-ARM64-Hot1X-Odin3-v0.13.0.zip"
CHECKSUM="${ASSET}.sha256"

case "$VISIBILITY" in
  public|private) ;;
  *) echo "Visibility must be public or private" >&2; exit 2 ;;
esac

command -v git >/dev/null || { echo "git is required" >&2; exit 1; }
command -v gh >/dev/null || { echo "GitHub CLI (gh) is required" >&2; exit 1; }

gh auth status >/dev/null

if [[ ! -d .git ]]; then
  git init -b main
fi

git add .
if ! git diff --cached --quiet; then
  git commit -m "Initial Odin 3 ARM64 Hot1X release"
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  gh repo create "$REPO_NAME" \
    "--$VISIBILITY" \
    --source=. \
    --remote=origin \
    --description="Self-contained LSFG-VK 2 Decky plugin for AYN Odin 3 ARM64 with live 1X passthrough"
fi

git push -u origin main

if gh release view "$VERSION" >/dev/null 2>&1; then
  gh release upload "$VERSION" "$ASSET" "$CHECKSUM" --clobber
else
  gh release create "$VERSION" \
    "$ASSET" "$CHECKSUM" \
    --title="$VERSION — Odin 3 ARM64 Hot 1X" \
    --notes-file=RELEASE_NOTES.md
fi

echo
gh repo view --web
