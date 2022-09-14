#!/usr/bin/env bash
set -e

PROTOSTAR_REPO="https://github.com/software-mansion/protostar"

function create_protostar_directory() {
    RETVAL=""

    local _protostar_dir=${_protostar_dir-"$HOME/.protostar"}
    mkdir -p "$_protostar_dir"

    RETVAL=$_protostar_dir
}

function get_platform_name() {
    RETVAL=""

    local _platform_name="$(uname -s)"
    case $_platform_name in
    Linux)
        RETVAL="Linux"
        ;;
    Darwin)
        RETVAL="macOS"
        ;;
    *)
        echo "unsupported platform: $PLATFORM"
        exit 1
        ;;
    esac
}

function get_requested_version() {
    RETVAL=""
    local _version=$1
    local _requested_ref=$2

    echo "Retrieving $_version version from $PROTOSTAR_REPO..."
    _response=$(curl -L -s -H 'Accept: application/json' "${PROTOSTAR_REPO}/releases/${_requested_ref}")
    if [ "$_response" == "{\"error\":\"Not Found\"}" ]; then
        echo "Version $_version not found"
        exit
    fi
    _requested_version=$(echo $_response | sed -e 's/.*"tag_name":"\([^"]*\)".*/\1/')
    echo "Using version $_requested_version"

    RETVAL=$_requested_version
}

function download_protostar() {
    RETVAL=""
    local _version=$1
    local _platform=$2
    local _output=$3

    local _requested_release_url="${PROTOSTAR_REPO}/releases/download/${_version}"
    local _protostar_tarball_name="protostar-${_platform}.tar.gz"
    local _tarball_download_url="${_requested_release_url}/${_protostar_tarball_name}"
    echo "Downloading protostar from ${_tarball_download_url}"
    curl -L $_tarball_download_url | tar -xvzC $_output
    local _protostar_binary_dir="${_output}/dist/protostar"
    local _protostar_binary="${_protostar_binary_dir}/protostar"
    chmod +x $_protostar_binary

    RETVAL=$_protostar_binary_dir
}

function add_protostar_to_path() {
    RETVAL=""
    local _protostar_binary_dir=$1

    local _profile
    local _pref_shell
    case $SHELL in
    */zsh)
        _profile=$HOME/.zshrc
        _pref_shell=zsh
        ;;
    */bash)
        _profile=$HOME/.bashrc
        _pref_shell=bash
        ;;
    */fish)
        _profile=$HOME/.config/fish/config.fish
        _pref_shell=fish
        ;;
    *)
        echo "error: could not detect shell, manually add ${_protostar_binary_dir} to your PATH."
        exit 1
        ;;
    esac

    if [[ ":$PATH:" != *":${_protostar_binary_dir}:"* ]]; then
        echo >>$_profile && echo "export PATH=\"\$PATH:$_protostar_binary_dir\"" >>$_profile
    fi
    echo && echo "Detected your preferred shell is ${_pref_shell} and added Protostar to PATH. Run 'source ${_profile}' or start a new terminal session to use Protostar."
    echo "Then, run 'protostar --help'."
}

function main() {
    local _provided_version_arg=$1
    local _requested_ref
    local _version

    if [ -n "$_provided_version_arg" ]; then
        _requested_ref="tag/v${_provided_version_arg}"
        _version=$_provided_version_arg
    else
        _requested_ref="latest"
        _version="latest"
    fi

    echo "Installing protostar"

    create_protostar_directory
    _protostar_dir=$RETVAL

    get_platform_name
    _platform_name=$RETVAL

    get_requested_version $_version $_requested_ref
    _requested_version=$RETVAL

    download_protostar $_requested_version $_platform_name $_protostar_dir
    _protostar_binary_dir=$RETVAL

    add_protostar_to_path $_protostar_binary_dir
}

while getopts ":v:" opt; do
    case $opt in
    v)
        PROVIDED_VERSION=$OPTARG
        ;;
    \?)
        echo "Invalid option: -$OPTARG" >&2
        exit 1
        ;;
    :)
        echo "Option -$OPTARG requires an argument." >&2
        exit 1
        ;;
    esac
done

main $PROVIDED_VERSION
