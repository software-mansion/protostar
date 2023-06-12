---
sidebar_label: Compilation
---

# Compiling a Cairo 1 Project with Protostar

To build your contracts, first define them in [`protostar.toml`](../05-protostar-toml.md#contracts-section)

To build run

```shell title="build"
protostar build
```

[Check CLI reference](../../cli-reference.md#build) for more details.

## Output directory

Running [`protostar build`](../../cli-reference.md#build) command will generate the compiled contracts in
the `build` directory by default.
You can specify a custom output directory using
the [`--compiled-contracts-dir`](../../cli-reference#compiled-contracts-dir-pathbuild-1) argument.

```shell title="Example"
$ protostar build --compiled-contracts-dir out
```

`.sierra.json` files contain contracts compiled to the sierra format. This format is used to declare contracts on
Starknet.
Read more about
sierra [here](https://docs.starknet.io/documentation/architecture_and_concepts/Contracts/cairo-1-and-sierra).

`.casm.json` files contain contracts compiled to the casm format which can be executed on the Cairo Virtual Machine. This
format is used to calculate `compiled_class_hash` of a contract.

`.class_hash` files contain class hash of the built contract

`.compiled_class_hash` files contain compiled class hash of the built contract

:::note
If you need to print machine-readable output in JSON format, you should use `--json` flag.
:::

## Compiling a single contract

If your `protostar.toml` file defines multiple contracts, and you wish to compile only one of them, you can specify
the [`--contract-name`](../../cli-reference.md#--contract-name-string-1) argument:

```
$ protostar build --contract-name my_contract
```
