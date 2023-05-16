#!/usr/bin/env bash

set -e

./scripts/install_cairo_bindings.sh "$@"
./scripts/install_protostar_rust_bindings.sh "$@"
