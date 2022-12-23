#!/usr/bin/env bash

./scripts/get_code_check_paths.sh | xargs black --check
