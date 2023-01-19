---
sidebar_label: Compilation
---

# Compiling a Project with Protostar

To compile your StarkNet contracts using Protostar, follow these steps:

1. Specify the contracts and their corresponding Cairo source files in the [`protostar.toml` configuration file](/docs/tutorials/configuration-file).
Each Cairo file that contains an entrypoint function should be listed in the [`contracts` section of the configuration file](/docs/tutorials/configuration-file#contracts).
An entrypoint is a function decorated with [`@constructor`](https://starknet.io/docs/hello_starknet/constructors.html), [`@external`](https://starknet.io/docs/hello_starknet/intro.html), [`@view`](https://starknet.io/docs/hello_starknet/intro.html), or [`@l1_handler`](https://starknet.io/docs/hello_starknet/l1l2.html?highlight=l1_handler).
If a Cairo file is imported by a file that is already included in the contracts section, it does not need to be listed separately.
For example: 
```toml title="protostar.toml"
# ...
[contracts]
main = ["./src/main.cairo"]
proxy = ["./src/proxy.cairo"]
```
2. Run the [`protostar build`](/docs/cli-reference#build) command.
This will generate the compiled contracts in the `build` directory by default.
You can specify a custom output directory using the [`compiled-contracts-dir`](/docs/cli-reference#--compiled-contracts-dir-pathbuild) argument.

```
$ protostar build --compiled-contracts-dir out
```

This will create the following files in the `out` directory:

```
protostar-project
├── src
│   ├── main.cairo
│   └── proxy.cairo
├── out
│   ├── main.json
│   ├── main_abi.json
│   ├── proxy.json
│   └── proxy_abi.json
└── protostar.toml
```


## Checking Cairo-lang version

Protostar ships with its own version of Cairo-lang and formatter, so you don't need to set up the environment separately. You can check the version of Cairo-lang that Protostar uses to compile your project by running `protostar -v`.

```console
$ protostar -v
Protostar version: X.Y.Z
Cairo-lang version: A.B.C
```
