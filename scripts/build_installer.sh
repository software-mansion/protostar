#!/usr/bin/env bash

kernel_name="$(uname -s)"
case $kernel_name in
Linux)
    platform_name="Linux"
    ;;
Darwin)
    platform_name="macOS"
    ;;
esac

hardware_name="$(uname -m)"

installer_filename="protostar-$platform_name-$hardware_name.tar.gz"

echo "PREPARING $installer_filename"
echo "[1/4] INSTALLING DEPS" && poetry install &>/dev/null &&
    echo "[2/4] BUILDING" && poe build &>/dev/null &&
    echo "[3/4] SMOKE TESTING: protostar -v" && ./dist/protostar/protostar -v &&
    echo "[4/4] COMPRESSING" && tar -czf $installer_filename ./dist/protostar
ls -lh $installer_filename

if [ $hardware_name == "arm64" ]; then
    echo ""
    echo "To publish the installer:"
    echo "1. Go to: https://github.com/software-mansion/protostar/releases/latest"
    echo "2. Click the 'Edit release' icon button"
    echo "3. Drag and drop $installer_filename"
    echo "4. Press 'Update release' button"
    echo ""
    echo "WARNING: Check if you are on the correct branch, branch is synchronized with remote, and tests are passing."
fi
