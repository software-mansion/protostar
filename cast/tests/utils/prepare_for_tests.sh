#!/bin/bash

if ! which starknet-devnet > /dev/null 2>&1; then
  echo "starknet-devnet not found, exiting."
  exit 1
fi

UTILS_DIRECTORY="$(git rev-parse --show-toplevel)/cast/tests/utils/"
CAIRO_REPO="https://github.com/starkware-libs/cairo/releases/download"
COMPILER_VERSION="v1.1.1"

SCARB_VERSION="0.4.1"

if [ ! -x "$COMPILER_DIRECTORY/cairo/bin/starknet-sierra-compile" ]; then
  if [[ $(uname -s) == 'Darwin' ]]; then
    wget "$CAIRO_REPO/$COMPILER_VERSION/release-aarch64-apple-darwin.tar" -P "$UTILS_DIRECTORY" || exit 1
    pushd "$UTILS_DIRECTORY"
    tar -xvf "$UTILS_DIRECTORY/release-aarch64-apple-darwin.tar" cairo/bin/starknet-sierra-compile || exit 1
    popd

  elif [[ $(uname -s) == 'Linux' ]]; then
    wget "$CAIRO_REPO/$COMPILER_VERSION/release-x86_64-unknown-linux-musl.tar.gz" -P "$UTILS_DIRECTORY" || exit 1
    pushd "$UTILS_DIRECTORY"
    tar -xzvf "$UTILS_DIRECTORY/release-x86_64-unknown-linux-musl.tar.gz" cairo/bin/starknet-sierra-compile || exit 1
    popd
  fi
fi

if command -v asdf &> /dev/null; then
  asdf plugin add scarb https://github.com/software-mansion/asdf-scarb.git
  asdf install scarb $SCARB_VERSION
  asdf global scarb $SCARB_VERSION
  scarb --version
else
  printf "Please install asdf\n https://asdf-vm.com/guide/getting-started.html#_2-download-asdf\n"
fi
