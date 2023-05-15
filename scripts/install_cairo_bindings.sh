#!/usr/bin/env bash

set -e

function install_dev() {
  git pull origin $(git rev-parse --abbrev-ref HEAD) --ff-only --recurse-submodules

  pushd cairo/crates/cairo-lang-python-bindings
  rustup override set nightly-2022-11-03 || return 1;
  maturin develop --release || return 1;
  popd
}

function install_prod() {
  git pull origin $(git rev-parse --abbrev-ref HEAD) --ff-only --recurse-submodules

  pushd cairo/crates/cairo-lang-python-bindings
  rustup override set nightly-2022-11-03 || return 1;
  maturin build || return 1;
  popd

  pushd cairo/target/wheels
  pip install "./$(ls | grep cairo_python_bindings)" || return 1;
  popd
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
