#!/usr/bin/env bash

find protostar -name '*.py' | xargs black --check
