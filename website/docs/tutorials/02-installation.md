---
sidebar_label: Installation
---

# Installation

Protostar is easy to install on Linux and Mac systems. In this section, we will walk through the process of installing and upgrading Protostar.

## Requirements
To use Protostar's dependency management commands, you must have git installed and added to your `$PATH` environment variable.

The `$PATH` is an environment variable that specifies a list of directories in which the system looks for executables.
If you do not have git in your `$PATH`, you will need to add the directory where git is installed in order to use Protostar.

## Linux and Mac
1. Open a terminal and run the following command:
```console
curl -L https://raw.githubusercontent.com/software-mansion/protostar/master/install.sh | bash
```
2. Close and reopen the terminal.
3. To check the version of Protostar and Cairo that you have installed, run `protostar -v`.

### Specifying version

If you want to install a specific version of Protostar, run the following command with the desired version number:

```console
curl -L https://raw.githubusercontent.com/software-mansion/protostar/master/install.sh | bash -s -- -v 0.3.2
```

## Windows Compatibility
Protostar is not currently supported on Windows.

# Upgrading Protostar
To upgrade Protostar, run:
```shell
protostar upgrade
```

# Protostar releases

Protostar follows a biweekly release schedule.
Each release may include new features, enhancements, bug fixes, deprecations and breaking changes.
For detailed information about each release, consult the [release notes](https://github.com/software-mansion/protostar/releases).
A link to the release notes for the latest version of Protostar will be displayed when a new release is available.

# How to build Protostar from source code
If you are unable to install Protostar using the instructions above, you can try building it from the [source code](https://github.com/software-mansion/protostar) as follows:

1. [Set up a development environment.](https://github.com/software-mansion/protostar#setting-up-environment)
1. Run `poe build`. This will create a `dist` directory.
1. Move the `dist` directory to the desired location (e.g. `~/.protostar`).
1. Add `DESIRED_LOCATION/dist/protostar` to the `PATH`.