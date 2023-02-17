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
  pushd "${1}"
  git clone https://github.com/software-mansion-labs/cairo.git
  pushd cairo
  # currrent master works ok, in case it doesn't, uncomment the line below
  # git checkout 6db822a167b0109c773ed8ee75118f975b58bec3 # working commit
  pushd crates/cairo-lang-python-bindings
  rustup override set nightly
  maturin develop --release || return 1;
  popd # cairo
  popd # cairo/crates/cairo_python_bindings
  popd # "${1}"
}

DIR=$(mktemp -d)
install $DIR && echo "DONE" || echo "installation failed"