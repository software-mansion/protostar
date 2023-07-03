#!/bin/bash

if ! which starknet-devnet > /dev/null 2>&1; then
  echo "starknet-devnet not found, exiting."
  exit 1
fi

DIRECTORY="$(git rev-parse --show-toplevel)/cast/tests/utils/"
CAIRO_REPO="https://github.com/starkware-libs/cairo/releases/download"
COMPILER_VERSION="v1.1.1"

SCARB_REPO="https://github.com/software-mansion/scarb/releases/download"
SCARB_VERSION="v0.4.1"

if [ ! -x "$COMPILER_DIRECTORY/cairo/bin/starknet-sierra-compile" ]; then
  if [[ $(uname -s) == 'Darwin' ]]; then
    wget "$CAIRO_REPO/$COMPILER_VERSION/release-aarch64-apple-darwin.tar" -P "$DIRECTORY" || exit 1
    pushd "$DIRECTORY"
    tar -xvf "$DIRECTORY/release-aarch64-apple-darwin.tar" cairo/bin/starknet-sierra-compile || exit 1
    popd

  elif [[ $(uname -s) == 'Linux' ]]; then
    wget "$CAIRO_REPO/$COMPILER_VERSION/release-x86_64-unknown-linux-musl.tar.gz" -P "$DIRECTORY" || exit 1
    pushd "$DIRECTORY"
    tar -xzvf "$DIRECTORY/release-x86_64-unknown-linux-musl.tar.gz" cairo/bin/starknet-sierra-compile || exit 1
    popd
  fi
fi

if [ ! -x "$COMPILER_DIRECTORY/scarb*/bin/scarb" ]; then
  if [[ $(uname -s) == 'Darwin' ]]; then
    wget "$SCARB_REPO/$SCARB_VERSION/scarb-$SCARB_VERSION-aarch64-apple-darwin.tar.gz" -P "$DIRECTORY" || exit 1
    pushd "$DIRECTORY"
    tar -xvf "$DIRECTORY/scarb-$SCARB_VERSION-aarch64-apple-darwin.tar.gz" scarb-$SCARB_VERSION-aarch64-apple-darwin/bin/scarb || exit 1
    popd

  elif [[ $(uname -s) == 'Linux' ]]; then
    wget "$CAIRO_REPO/$COMPILER_VERSION/scarb-$SCARB_VERSION-x86_64-unknown-linux-musl.tar.gz" -P "$DIRECTORY" || exit 1
    pushd "$DIRECTORY"
    tar -xzvf "$DIRECTORY/scarb-$SCARB_VERSION-x86_64-unknown-linux-musl.tar.gz" scarb-$SCARB_VERSION-aarch64-apple-darwin/bin/scarb || exit 1
    popd
  fi
fi

pushd "$DIRECTORY/../data/contracts/balance"
"$DIRECTORY"scarb-$SCARB_VERSION-aarch64-apple-darwin/bin/scarb build

