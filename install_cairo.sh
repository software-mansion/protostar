#!/usr/bin/env bash

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
  # currrent master works ok, in case it doesn't, uncomment the line below
  git checkout 5608ce7e052df79da11485689cb5f1459d3e5d18 # working commit
  pushd crates/cairo-lang-python-bindings
  rustup override set nightly
  maturin develop --release
  popd # cairo
  popd # cairo/crates/cairo_python_bindings
  popd # "${1}"
}

DIR=$(mktemp -d)
install $DIR && echo "DONE" || echo "installation failed"
