#!/usr/bin/env bash
set -e

if [ -n "$(git status --porcelain)" ]; then
  >&2 echo "Working tree has uncommited changes, please stash/commit them before bumping submodule version"
  exit 1
fi

tracking_branch="$(git for-each-ref --format='%(upstream:short)' "$(git symbolic-ref -q HEAD)")"

if [ $tracking_branch == "origin/master" ] ; then
  >&2 echo "You are currently tracking master branch. Checkout to another branch before bumping submodule version"
  exit 1
fi


git submodule update --recursive --remote --init cairo
git add ./cairo
git commit -m "Bump cairo bindings" --no-verify