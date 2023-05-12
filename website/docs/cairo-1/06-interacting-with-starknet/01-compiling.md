---
sidebar_label: Compilation
---

# Compiling a Cairo 1 Project with Protostar

To build your contracts, first define them in [`protostar.toml`](../04-protostar-toml.md#contracts-section)

To build run

```shell title="build-cairo1"
protostar build-cairo1
```

[Check CLI reference](../../cli-reference.md#build-cairo1) for more details.

## Output directory

Running [`protostar build-cairo1`](../../cli-reference.md#build-cairo1) command will generate the compiled contracts in
the `build` directory by default.
You can specify a custom output directory using
the [`--compiled-contracts-dir`](../../cli-reference#compiled-contracts-dir-pathbuild-1) argument.

```shell title="Example"
$ protostar build-cairo1 --compiled-contracts-dir out
```

`.sierra.json` files contain contracts compiled to the sierra format. This format is used to declare contracts on
Starknet.
Read more about
sierra [here](https://docs.starknet.io/documentation/architecture_and_concepts/Contracts/cairo-1-and-sierra).

`.casm.json` files contain contracts compiled to the casm format which can be executed on the cairo virtual machine. This
format is used to calculate `compiled_class_hash` of a contract.

## Using external dependencies

If your build requires using external dependencies, you can specify additional paths in the `build-cairo1` command. To
do that, you need to use the [`--linked-libraries`](../../cli-reference.md#linked-libraries-path) argument like this:

```
$ protostar build-cairo1 --linked-libraries /path/to/the/external/lib
```

:::note
Provided paths must contain correctly formatted cairo packages, otherwise build will fail.
:::

## Compiling a single contract

If your `protostar.toml` file defines multiple contracts and you wish to compile only one of them, you can specify
the [`--contract-name`](../../cli-reference.md#--contract-name-string-1) argument:

```
$ protostar build-cairo1 --contract-name my_contract
```
