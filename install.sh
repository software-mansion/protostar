#!/usr/bin/env bash
set -e

PROTOSTAR_REPO="https://github.com/software-mansion/protostar"
RESULT=""

function get_platform_name() {
    _platform_name="$(uname -s)"
    case $_platform_name in
    Linux)
        RESULT="Linux"
        ;;
    Darwin)
        RESULT="macOS"
        ;;
    *)
        echo "unsupported platform: $PLATFORM"
        exit 1
        ;;
    esac
}

function get_requested_version() {
    _version=$1
    _requested_ref=$2
    RESULT=""

    echo "Retrieving $_version version from $PROTOSTAR_REPO..."
    _response=$(curl -L -s -H 'Accept: application/json' "${PROTOSTAR_REPO}/releases/${_requested_ref}")
    if [ "$_response" == "{\"error\":\"Not Found\"}" ]; then
        echo "Version $_version not found"
        exit
    fi
    RESULT=$(echo $_response | sed -e 's/.*"tag_name":"\([^"]*\)".*/\1/')
    echo "Using version $RESULT"
}

function download_protostar() {
    _version=$1
    _platform=$2
    _output=$3

    _requested_release_url="${PROTOSTAR_REPO}/releases/download/${_version}"
    _protostar_tarball_name="protostar-${_platform}.tar.gz"
    _tarball_download_url="${_requested_release_url}/${_protostar_tarball_name}"
    echo "Downloading protostar from ${_tarball_download_url}"
    curl -L $_tarball_download_url | tar -xvzC $PROTOSTAR_DIR
}

while getopts ":v:" opt; do
    case $opt in
    v)
        PROVIDED_VERSION=$OPTARG
        ;;
    \?)
        echo "Invalid option: -$OPTARG" >&2
        exit 1
        ;;
    :)
        echo "Option -$OPTARG requires an argument." >&2
        exit 1
        ;;
    esac
done

echo "Installing protostar"

PROTOSTAR_DIR=${PROTOSTAR_DIR-"$HOME/.protostar"}
mkdir -p "$PROTOSTAR_DIR"

get_platform_name
PLATFORM=$RESULT

if [ -n "$PROVIDED_VERSION" ]; then
    REQUESTED_REF="tag/v${VERSION}"
    VERSION=$PROVIDED_VERSION
else
    REQUESTED_REF="latest"
    VERSION="latest"
fi

get_requested_version $VERSION $REQUESTED_REF
REQUESTED_VERSION=$RESULT

download_protostar $REQUESTED_VERSION $PLATFORM $PROTOSTAR_DIR

PROTOSTAR_BINARY_DIR="${PROTOSTAR_DIR}/dist/protostar"
PROTOSTAR_BINARY="${PROTOSTAR_BINARY_DIR}/protostar"
chmod +x $PROTOSTAR_BINARY

case $SHELL in
*/zsh)
    PROFILE=$HOME/.zshrc
    PREF_SHELL=zsh
    ;;
*/bash)
    PROFILE=$HOME/.bashrc
    PREF_SHELL=bash
    ;;
*/fish)
    PROFILE=$HOME/.config/fish/config.fish
    PREF_SHELL=fish
    ;;
*)
    echo "error: could not detect shell, manually add ${PROTOSTAR_BINARY_DIR} to your PATH."
    exit 1
    ;;
esac

if [[ ":$PATH:" != *":${PROTOSTAR_BINARY_DIR}:"* ]]; then
    echo >>$PROFILE && echo "export PATH=\"\$PATH:$PROTOSTAR_BINARY_DIR\"" >>$PROFILE
fi

echo && echo "Detected your preferred shell is ${PREF_SHELL} and added protostar to PATH. Run 'source ${PROFILE}' or start a new terminal session to use protostar."
echo "Then, simply run 'protostar --help' "
