#!/usr/bin/env bash
set -e

PROTOSTAR_REPO="https://github.com/software-mansion/protostar"
RESULT=""

function get_platform_name() {
    RESULT=""
    _platform_name="$(uname -s)"
    case $_platform_name in
    Linux)
        RESULT="Linux"
        ;;
    Darwin)
        RESULT="macOS"
        ;;
    *)
        echo "unsupported platform: $PLATFORM"
        exit 1
        ;;
    esac
}

function get_requested_version() {
    RESULT=""
    _version=$1
    _requested_ref=$2

    echo "Retrieving $_version version from $PROTOSTAR_REPO..."
    _response=$(curl -L -s -H 'Accept: application/json' "${PROTOSTAR_REPO}/releases/${_requested_ref}")
    if [ "$_response" == "{\"error\":\"Not Found\"}" ]; then
        echo "Version $_version not found"
        exit
    fi
    RESULT=$(echo $_response | sed -e 's/.*"tag_name":"\([^"]*\)".*/\1/')
    echo "Using version $RESULT"
}

function download_protostar() {
    RESULT=""
    _version=$1
    _platform=$2
    _output=$3

    _requested_release_url="${PROTOSTAR_REPO}/releases/download/${_version}"
    _protostar_tarball_name="protostar-${_platform}.tar.gz"
    _tarball_download_url="${_requested_release_url}/${_protostar_tarball_name}"
    echo "Downloading protostar from ${_tarball_download_url}"
    curl -L $_tarball_download_url | tar -xvzC $_output
    _protostar_binary_dir="${_output}/dist/protostar"
    _protostar_binary="${_protostar_binary_dir}/protostar"
    chmod +x $_protostar_binary
    RESULT=$_protostar_binary_dir
}

function add_protostar_to_path() {
    _protostar_binary_dir=$1

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
    echo && echo "Detected your preferred shell is ${_pref_shell} and added protostar to PATH. Run 'source ${_profile}' or start a new terminal session to use protostar."
    echo "Then, simply run 'protostar --help' "
}

function main() {
    _provided_version_arg=$1

    if [ -n "$_provided_version_arg" ]; then
        _requested_ref="tag/v${_provided_version_arg}"
        version=$_provided_version_arg
    else
        _requested_ref="latest"
        version="latest"
    fi

    echo "Installing protostar"
    protostar_dir=${protostar_dir-"$HOME/.protostar"}
    mkdir -p "$protostar_dir"

    get_platform_name
    platform_name=$RESULT

    get_requested_version $version $_requested_ref
    _requested_version=$RESULT

    download_protostar $_requested_version $platform_name $protostar_dir
    _protostar_binary_dir=$RESULT

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
