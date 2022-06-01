---
sidebar_label: Installation (1 min)
---

# Installation

## Requirements
Protostar requires a [git](https://git-scm.com/) executable (>= 2.28) to be specified in the `$PATH`.

## Linux and Mac
1. Copy and run in a terminal the following command:
```console
curl -L https://raw.githubusercontent.com/software-mansion/protostar/master/install.sh | bash
```
2. Restart the terminal.
3. Run `protostar -v` to check Protostar and [cairo-lang](https://pypi.org/project/cairo-lang/) version.


## Windows
Not supported. 

# Upgrading Protostar
To upgrade Protostar, run:
```shell
$ protostar upgrade
```

# How to build Protostar from source code
If your platform isn't supported or installation fails, you can try building Protostar from [source code](https://github.com/software-mansion/protostar) in the following way:

1. [Set up a development environment.](https://github.com/software-mansion/protostar#setting-up-environment)
1. Run `poe build`. The result of running this command should be the `dist` directory.
1. Move the `dist` directory to the desired location (e.g. `~/.protostar`).
1. Add `DESIRED_LOCATION/dist/protostar` to the `PATH`.