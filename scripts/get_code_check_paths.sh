#!/usr/bin/env bash
set -e

if [ "$#" != 1 ]; then
  echo "Invalid number of arguments, expected 1: lint/format";
  exit 1;
fi;

if [ "$1" == "lint" ]; then
  find . -name '*.py'
elif [ "$1" == "format" ]; then
  find protostar -name '*.py'
else
  echo "Invalid argument provided, expected: lint/format";
  exit 1;
fi;

