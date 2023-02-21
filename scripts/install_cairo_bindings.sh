#!/usr/bin/env bash

set -e

# clean up
if [ "$1" == "--cleanup" ]; then
  poetry env info -p | xargs rm -rf
  if [[ $(uname -m) == 'arm64' ]]; then
    CFLAGS=-I/opt/homebrew/opt/gmp/include LDFLAGS=-L/opt/homebrew/opt/gmp/lib poetry install
  else
    poetry install
  fi
fi

function install() {
  git submodule update --init --recursive

  pushd cairo
  pushd crates/cairo-lang-python-bindings
  rustup override set nightly
  maturin develop --release || return 1;
  popd # cairo
  popd # cairo/crates/cairo_python_bindings
}

install && echo "DONE" || echo "installation failed"
