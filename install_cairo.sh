#!/bin/bash

set -e

# clean up
if [ "$1" == "--cleanup" ]; then
  poetry env info -p | xargs rm -rf
  CFLAGS=-I/opt/homebrew/opt/gmp/include LDFLAGS=-L/opt/homebrew/opt/gmp/lib poetry install
fi

function install() {
  pushd "${1}"
  git clone https://github.com/software-mansion-labs/cairo.git
  pushd cairo
  git checkout 91ac2eed4e8bf3bd92f864a0bb3c86711f251446 # working commit
  pushd crates/cairo_python_bindings
  rustup override set nightly
  pip install maturin
  maturin develop --release
  popd # cairo
  popd # cairo/crates/cairo_python_bindings
  popd # "${1}"
}


DIR=$(poetry env info -p)
install $DIR || echo "installation failed"

echo "DONE"
