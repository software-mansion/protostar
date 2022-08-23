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

SHELL_MOCK=$2
exit_if_empty "SHELL_MOCK" $SHELL_MOCK

function uname_mock() {
    read -p "[uname$(printf ' %s' "$@")]: " response
    echo $response
}

function curl_mock() {
    read -p "[curl$(printf ' %s' "$@")]: " response
    echo $response
}

function run_script() {
    source ./install.sh
}

function run_mocked_script() {
    HOME=$HOME_MOCK
    SHELL=$SHELL_MOCK
    alias uname=uname_mock
    alias curl=curl_mock
    run_script
}

function tar() {
    read response
    echo "[tar $response]"
}

run_mocked_script
