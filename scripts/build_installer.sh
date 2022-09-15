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
echo "INSTALLING DEPS 1/3" && poetry install &>/dev/null &&
    echo "BUILDING 2/3" && poe build &>/dev/null &&
    echo "COMPRESSING 3/3" && tar -czf $installer_filename ./dist/protostar
ls -lh $installer_filename
