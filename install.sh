#!/usr/bin/env bash
set -e

echo Installing protostar

PROTOSTAR_DIR=${PROTOSTAR_DIR-"$HOME/.protostar"}
PROTOSTAR_BIN_DIR="$PROTOSTAR_DIR/bin"
mkdir -p "$PROTOSTAR_BIN_DIR"


PLATFORM="$(uname -s)"
case $PLATFORM in
  Linux)
    PLATFORM="Linux"
    ;;
  Darwin)
    PLATFORM="macOS"
    ;;
  *)
    echo "unsupported platform: $PLATFORM"
    exit 1
    ;;
esac

PROTOSTAR_REPO="https://github.com/software-mansion/protostar"

echo Retrieving the latest version from $PROTOSTAR_REPO...

LATEST_RELEASE=$(curl -L -s -H 'Accept: application/json' "${PROTOSTAR_REPO}/releases/latest")
LATEST_VERSION=$(echo $LATEST_RELEASE | sed -e 's/.*"tag_name":"\([^"]*\)".*/\1/')

echo Using version $LATEST_VERSION

LATEST_RELEASE_URL="${PROTOSTAR_REPO}/releases/download/${LATEST_VERSION}"
PROTOSTAR_EXECUTABLE_NAME="protostar-${PLATFORM}"
BINARY_DOWNLOAD_URL="${LATEST_RELEASE_URL}/${PROTOSTAR_EXECUTABLE_NAME}"

echo "Downloading binary from ${BINARY_DOWNLOAD_URL}"
curl -L $BINARY_DOWNLOAD_URL --output protostar

BINARY_DESTINATION="${PROTOSTAR_BIN_DIR}/protostar"
mv "./protostar" $BINARY_DESTINATION
chmod +x $BINARY_DESTINATION

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
    echo "error: could not detect shell, manually add ${PROTOSTAR_BIN_DIR} to your PATH."
    exit 1
esac

if [[ ":$PATH:" != *":${PROTOSTAR_BIN_DIR}:"* ]]; then
    echo >> $PROFILE && echo "export PATH=\"\$PATH:$PROTOSTAR_BIN_DIR\"" >> $PROFILE
fi

echo && echo "Detected your preferred shell is ${PREF_SHELL} and added protostar to PATH. Run 'source ${PROFILE}' or start a new terminal session to use protostar."
echo "Then, simply run 'protostar' "