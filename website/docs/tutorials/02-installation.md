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
3. Run `protostar -v`.

```console title="Protostar should print its and cairo-lang version."
Protostar version: 0.1.0
Cairo-lang version: 0.8.1
```

## Windows
Not supported. 

# Upgrading Protostar
To upgrade Protostar, run:
```shell
$ protostar upgrade
```