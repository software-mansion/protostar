#!/usr/bin/env bash
set -e

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

echo Installing protostar

PROTOSTAR_DIR=${PROTOSTAR_DIR-"$HOME/.protostar"}
mkdir -p "$PROTOSTAR_DIR"

get_platform_name
PLATFORM=$RESULT

while getopts ":v:" opt; do
    case $opt in
    v)
        VERSION=$OPTARG
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

if [ -n "$VERSION" ]; then
    REQUESTED_REF="tag/v${VERSION}"
else
    REQUESTED_REF="latest"
    VERSION="latest"
fi

PROTOSTAR_REPO="https://github.com/software-mansion/protostar"

echo Retrieving $VERSION version from $PROTOSTAR_REPO...

REQUESTED_RELEASE=$(curl -L -s -H 'Accept: application/json' "${PROTOSTAR_REPO}/releases/${REQUESTED_REF}")

if [ "$REQUESTED_RELEASE" == "{\"error\":\"Not Found\"}" ]; then
    echo "Version $VERSION not found"
    exit
fi

REQUESTED_VERSION=$(echo $REQUESTED_RELEASE | sed -e 's/.*"tag_name":"\([^"]*\)".*/\1/')

echo Using version $REQUESTED_VERSION

REQUESTED_RELEASE_URL="${PROTOSTAR_REPO}/releases/download/${REQUESTED_VERSION}"
PROTOSTAR_TARBALL_NAME="protostar-${PLATFORM}.tar.gz"
TARBALL_DOWNLOAD_URL="${REQUESTED_RELEASE_URL}/${PROTOSTAR_TARBALL_NAME}"

echo "Downloading protostar from ${TARBALL_DOWNLOAD_URL}"
curl -L $TARBALL_DOWNLOAD_URL | tar -xvzC $PROTOSTAR_DIR

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
