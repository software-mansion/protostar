#!/usr/bin/env bash

set -e

function install_dev() {
  git submodule update --init --recursive
  git pull origin $(git rev-parse --abbrev-ref HEAD) --ff-only --recurse-submodules

  pushd cairo-protostar/crates/cairo-lang-python-bindings
  rustup override set nightly-2023-06-01 || return 1;
  maturin develop --release || return 1;
  popd
}

function install_prod() {
  git submodule update --init --recursive
  git pull origin $(git rev-parse --abbrev-ref HEAD) --ff-only --recurse-submodules

  pushd cairo-protostar/crates/cairo-lang-python-bindings
  rustup override set nightly-2023-06-01 || return 1;
  maturin build || return 1;
  popd # cairo/crates/cairo-lang-python-bindings

  pushd cairo/target/wheels
  pip install "./$(ls | grep cairo_python_bindings)" || return 1;
  popd # cairo/target/wheels
}

if [ "$1" == "prod" ]; then
    if install_prod; then
      echo "DONE"
    else
      echo "installation failed"
      exit 1
    fi
  else
    if install_dev; then
      echo "DONE"
    else
      echo "installation failed"
      exit 1
    fi
fi
