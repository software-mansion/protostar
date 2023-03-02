#!/usr/bin/env bash
set -e

git submodule update --recursive --remote --init cairo
git add ./cairo
git commit -m "Bump cairo bindings" --no-verify