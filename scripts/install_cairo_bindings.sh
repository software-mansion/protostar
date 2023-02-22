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

function install_dev() {
  git pull --recurse-submodules
  git submodule update --remote --recursive --init

  pushd cairo
  pushd crates/cairo-lang-python-bindings
  rustup override set nightly || return 1;
  maturin develop --release || return 1;
  popd # cairo
  popd # cairo/crates/cairo_python_bindings
}

function install_prod() {
  git submodule update --init --recursive

  pushd cairo
  pushd crates/cairo-lang-python-bindings
  rustup override set nightly || return 1;
  maturin build || return 1;
  popd # cairo
  pip install $(ls ./target/wheels | grep cairo_python_bindings)
  popd # cairo/crates/cairo_python_bindings
}

if [ "$1" == "prod" ]; then
    install_prod && echo "DONE" || echo "installation failed" && exit 1
  else
    install_dev && echo "DONE" || echo "installation failed" && exit 1
fi


