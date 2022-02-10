#!/usr/bin/env bash
set -e

echo Installing protostar

PROTOSTAR_DIR=${PROTOSTAR_DIR-"$HOME/.protostar"}
PROTOSTAR_BIN_DIR="$PROTOSTAR_DIR/bin"
mkdir -p $PROTOSTAR_BIN_DIR

PROTOSTAR_REPO="https://github.com/arcticae/testrepo" # TODO: Pull binary from repo

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