#!/bin/bash

if ! which starknet-devnet > /dev/null 2>&1; then
  echo "starknet-devnet not found, exiting."
  exit 1
fi

COMPILER_DIRECTORY="$(git rev-parse --show-toplevel)/cast/tests/utils/"
CAIRO_REPO="https://github.com/starkware-libs/cairo/releases/download"
COMPILER_VERSION="v1.0.0"

if [ ! -x "$COMPILER_DIRECTORY/starknet-sierra-compile" ]; then
  if [[ $(uname -s) == 'Darwin' ]]; then
    wget "$CAIRO_REPO/$COMPILER_VERSION/release-aarch64-apple-darwin.tar" -P "$COMPILER_DIRECTORY" || exit 1
    pushd "$COMPILER_DIRECTORY"
    tar -xvf "$COMPILER_DIRECTORY/release-aarch64-apple-darwin.tar" cairo/bin/starknet-sierra-compile || exit 1
    popd
  elif [[ $(uname -s) == 'Linux' ]]; then
    wget "$CAIRO_REPO/$COMPILER_VERSION/release-x86_64-unknown-linux-musl.tar.gz" -P "$COMPILER_DIRECTORY" || exit 1
    pushd "$COMPILER_DIRECTORY"
    tar -xzvf "$COMPILER_DIRECTORY/release-x86_64-unknown-linux-musl.tar.gz" cairo/bin/starknet-sierra-compile || exit 1
    popd
  fi
fi
