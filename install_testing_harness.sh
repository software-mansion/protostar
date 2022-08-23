#!/usr/bin/env bash

function exit_if_empty() {
    arg_name=$1
    arg_value=$2

    if [[ ! $arg_value ]]; then
        echo "Missing positional argument: $arg_name"
        exit 1
    fi
}

HOME_MOCK=$1
exit_if_empty "HOME_MOCK" $HOME_MOCK

PLATFORM_MOCK=$2
exit_if_empty "PLATFORM_MOCK" $PLATFORM_MOCK

SHELL_MOCK=$3
exit_if_empty "SHELL_MOCK" $SHELL_MOCK

function curl_mock() {
    printf "<curl>"
    printf '%s ' "$@"
    printf "</curl>"
}

function tar_mock() {
    printf "<tar>"
    printf '%s ' "$@"
    printf "</tar>"
}

function run_script() {
    source ./install.sh
}

function run_mocked_script() {
    HOME=$HOME_MOCK
    PLATFORM=$PLATFORM_MOCK
    SHELL=$SHELL_MOCK
    alias curl=curl_mock
    alias tar=tar_mock
    run_script
}

run_mocked_script
