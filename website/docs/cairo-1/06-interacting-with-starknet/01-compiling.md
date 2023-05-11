---
sidebar_label: Compilation
---

# Compiling a Cairo 1 Project with Protostar

To compile your Starknet contracts written in Cairo 1 using Protostar, follow these steps:

1. [Prepare your contracts](09-scripting.md).
2. Specify the contracts in the [`protostar.toml` configuration file](../04-protostar-toml.md).
Each Cairo file that contains an entrypoint function should be listed in the [`contracts` section of the configuration file](../04-protostar-toml.md#contracts-section).
An entrypoint is a function decorated with `#[external]` or `#[view]`.
3. Run the [`protostar build-cairo1`](../../cli-reference.md#build-cairo1) command.

`build-cairo1` command outputs class hash and compiled class hash if the compilation is successful.

## Output directory

Running [`protostar build-cairo1`](../../cli-reference.md#build-cairo1) command will generate the compiled contracts in the `build` directory by default.
You can specify a custom output directory using the [`--compiled-contracts-dir`](../../cli-reference#compiled-contracts-dir-pathbuild-1) argument.

```
$ protostar build-cairo1 --compiled-contracts-dir out
```

This will create the following files in the `out` directory:

```
protostar-project
├── src
│   ├── main.cairo
│   └── proxy.cairo
├── out
│   ├── main.casm.json
│   ├── main.sierra.json
│   ├── main.class.hash
│   ├── main.compiled.class.hash
│   ├── proxy.casm.json
│   ├── proxy.sierra.json
│   ├── proxy.class.hash
│   ├── proxy.compiled.class.hash
└── protostar.toml
```

`.sierra.json` files contain contracts compiled to the sierra format which allows provable reverted transactions. Read more about sierra [here](https://docs.starknet.io/documentation/architecture_and_concepts/Contracts/cairo-1-and-sierra).

`.casm.json` files contain contracts compiled to the casm format which can be executed on the virtual machine.

`.class.hash` files contain class hash of the built contract

`.compiled.class.hash` files contain compiled class hash of the built contract

## External libraries

If you want to attach external libraries to the build, you can specify additional paths that will be searched for the cairo libraries (library is just a cairo [package](../02-understanding-cairo-packages.md)). To do that, you need to use the [`--linked-libraries`](../../cli-reference.md#linked-libraries-path) argument like this:

```
$ protostar build-cairo1 --linked-libraries /path/to/the/external/lib
```

Please note, that specified directories have to contain properly prepared libraries, otherwise an error will be raised.

## Compiling a single contract

If you wish to compile only one contract, you can use the [`--contract-name`](../../cli-reference.md#contract-name-string-1) argument:

```
$ protostar build-cairo1 --contract-name my_contract
```

In such a case, if your `protostar.toml` looks like this:

```
[contracts]
main = ["src/main.cairo"]
proxy = ["src/proxy.cairo"]
my_contract = ["src/my_contract.cairo"]
```

only the contract called `my_contract` will be compiled.
