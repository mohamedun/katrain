#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."
export KATRAIN_APP_NAME="KaTrain Territory"
export KATRAIN_BUNDLE_ID="org.mohamedun.katrain.territory"
export KATRAIN_VERSION="1.20.0"
# Reuse the native engine from an official KaTrain installation. PyInstaller
# collects its dependent libraries into the new app, so it runs independently.
export KATRAIN_KATAGO_BINARY="${KATRAIN_KATAGO_BINARY:-/Applications/KaTrain.app/Contents/Frameworks/katrain/KataGo/katago-osx}"
if [[ ! -f "$KATRAIN_KATAGO_BINARY" ]]; then
    echo "Set KATRAIN_KATAGO_BINARY to a native macOS KataGo executable."
    exit 1
fi

# Sign outside cloud-synced folders, which can add Finder metadata to app bundles.
build_dir=$(mktemp -d /private/tmp/katrain-territory.XXXXXX)
trap 'rm -rf "$build_dir"' EXIT

if [[ -x .venv/bin/pyinstaller ]]; then
    .venv/bin/pyinstaller spec/KaTrain.spec --clean --noconfirm --distpath "$build_dir/dist" --workpath "$build_dir/build"
else
    uv run pyinstaller spec/KaTrain.spec --clean --noconfirm --distpath "$build_dir/dist" --workpath "$build_dir/build"
fi
# Finder metadata inherited from local source files can prevent ad-hoc signing.
# Remove only that metadata from the newly generated bundle.
xattr -dr com.apple.FinderInfo "$build_dir/dist/$KATRAIN_APP_NAME.app"
xattr -dr com.apple.ResourceFork "$build_dir/dist/$KATRAIN_APP_NAME.app"
codesign --force --deep --sign - "$build_dir/dist/$KATRAIN_APP_NAME.app"
mkdir -p dist
ditto --norsrc --noextattr "$build_dir/dist/$KATRAIN_APP_NAME.app" "dist/$KATRAIN_APP_NAME.app"
echo "Built: $PWD/dist/$KATRAIN_APP_NAME.app"
