hardware_name="$(uname -m)"

if [ "$hardware_name" != "arm64" ]; then
    echo "Wrong hardware: $hardware_name. Expected arm64."
    exit 1
fi

poetry install
poe build
tar -czvf protostar-macOS-arm64.tar.gz ./dist/protostar
