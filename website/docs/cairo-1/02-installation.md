---
sidebar_label: Installation
---

# Installation

Protostar is easy to install on Linux and Mac systems. In this section, we will walk through the process of installing and upgrading Protostar.

### Linux and Mac
1. Open a terminal and run the following command:
```console
curl -L https://raw.githubusercontent.com/software-mansion/protostar/master/install.sh | bash
```
2. Close and reopen the terminal.
3. To check if the Protostar is installed correctly, run `protostar -v`.

### Specifying version

If you want to install a specific version of Protostar, run the following command with the desired version number:

```console
curl -L https://raw.githubusercontent.com/software-mansion/protostar/master/install.sh | bash -s -- -v 0.3.2
```

### Windows Compatibility
Protostar is not currently supported on Windows.

## Upgrading Protostar
To upgrade Protostar, run:
```shell
protostar upgrade
```
Protostar will inform you when a new version is available.


## How to build Protostar from source code
If you are unable to install Protostar using the instructions above, you can try building it from the [source code](https://github.com/software-mansion/protostar) as follows:

1. [Set up a development environment.](https://github.com/software-mansion/protostar#setting-up-environment)
1. Run `poe build`. This will create a `dist` directory.
1. Move the `dist` directory to the desired location (e.g. `~/.protostar`).
1. Add `DESIRED_LOCATION/dist/protostar` to the `PATH`.