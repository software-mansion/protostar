#!/usr/bin/env bash

function exit_if_empty() {
    arg_name=$1
    arg_value=$2

    if [[ ! $arg_value ]]; then
        echo "Missing positional argument: $arg_name"
        exit 1
    fi
}

exit_if_empty "HOME_MOCK" $1
HOME=$1

exit_if_empty "SHELL_MOCK" $2
SHELL=$2

VERSION=$3

function uname() {
    read -p "[uname$(printf ' %s' "$@")]: " response
    echo $response
}

function curl() {
    read -p "[curl$(printf ' %s' "$@")]: " response
    echo $response
}

function tar() {
    read response
    echo "[tar $response]"
}

if [ -n "$VERSION" ]; then
    source ./install.sh -v $VERSION
else
    source ./install.sh
fi
