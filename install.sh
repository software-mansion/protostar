#!/usr/bin/env bash
set -e

echo Installing protostar

PROTOSTAR_DIR=${PROTOSTAR_DIR-"$HOME/.protostar"}
mkdir -p "$PROTOSTAR_DIR"


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
  DESIRED_VERSION="tag/v${VERSION}"
else
  DESIRED_VERSION="latest"
  VERSION="latest"
fi

PROTOSTAR_REPO="https://github.com/software-mansion/protostar"

echo Retrieving $VERSION version from $PROTOSTAR_REPO...

DESIRED_RELEASE=$(curl -L -s -H 'Accept: application/json' "${PROTOSTAR_REPO}/releases/${DESIRED_VERSION}")

if [ "$DESIRED_RELEASE" == "{\"error\":\"Not Found\"}" ]; then
  echo "Version $VERSION not found"
  exit
fi

DESIRED_VERSION=$(echo $DESIRED_RELEASE | sed -e 's/.*"tag_name":"\([^"]*\)".*/\1/')

echo Using version $DESIRED_VERSION

DESIRED_RELEASE_URL="${PROTOSTAR_REPO}/releases/download/${DESIRED_VERSION}"
PROTOSTAR_TARBALL_NAME="protostar-${PLATFORM}.tar.gz"
TARBALL_DOWNLOAD_URL="${DESIRED_RELEASE_URL}/${PROTOSTAR_TARBALL_NAME}"

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
esac

if [[ ":$PATH:" != *":${PROTOSTAR_BINARY_DIR}:"* ]]; then
    echo >> $PROFILE && echo "export PATH=\"\$PATH:$PROTOSTAR_BINARY_DIR\"" >> $PROFILE
fi

echo && echo "Detected your preferred shell is ${PREF_SHELL} and added protostar to PATH. Run 'source ${PROFILE}' or start a new terminal session to use protostar."
echo "Then, simply run 'protostar --help' "