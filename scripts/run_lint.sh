#!/usr/bin/env bash

find . -name '*.py' | xargs pylint
