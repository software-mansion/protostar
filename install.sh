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
    local version=$1
    local platform=$2
    local output=$3

    local requested_release_url="${PROTOSTAR_REPO}/releases/download/${version}"
    local protostar_tarball_name="protostar-${platform}.tar.gz"
    local tarball_download_url="${requested_release_url}/${protostar_tarball_name}"
    echo "Downloading protostar from ${tarball_download_url}"
    curl -L $tarball_download_url | tar -xvzC $output
    local protostar_binary_dir="${output}/dist/protostar"
    local protostar_binary="${protostar_binary_dir}/protostar"
    chmod +x $protostar_binary

    RETVAL=$protostar_binary_dir
}

function add_protostar_to_path() {
    RETVAL=""
    local protostar_binary_dir=$1

    local profile
    local pref_shell
    case $SHELL in
    */zsh)
        profile=$HOME/.zshrc
        pref_shell=zsh
        ;;
    */bash)
        profile=$HOME/.bashrc
        pref_shell=bash
        ;;
    */fish)
        profile=$HOME/.config/fish/config.fish
        pref_shell=fish
        ;;
    *)
        echo "error: could not detect shell, manually add ${protostar_binary_dir} to your PATH."
        exit 1
        ;;
    esac

    if [[ ":$PATH:" != *":${protostar_binary_dir}:"* ]]; then
        echo >>$profile && echo "export PATH=\"\$PATH:$protostar_binary_dir\"" >>$profile
    fi
    echo && echo "Detected your preferred shell is ${pref_shell} and added Protostar to PATH. Run 'source ${profile}' or start a new terminal session to use Protostar."
    echo "Then, run 'protostar --help'."
}

function main() {
    local provided_version_arg=$1

    local requested_ref
    local version
    if [ -n "$provided_version_arg" ]; then
        requested_ref="tag/v${provided_version_arg}"
        version=$provided_version_arg
    else
        requested_ref="latest"
        version="latest"
    fi

    echo "Installing protostar"

    get_platform_name
    platform_name=$RETVAL

    get_requested_version $version $requested_ref
    requested_version=$RETVAL

    create_protostar_directory
    protostar_dir=$RETVAL

    download_protostar $requested_version $platform_name $protostar_dir
    protostar_binary_dir=$RETVAL

    add_protostar_to_path $protostar_binary_dir
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
