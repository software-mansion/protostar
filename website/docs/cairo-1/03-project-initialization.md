---
sidebar_label: Project initialization
---

# Project initialization

## Creating a project

To create a new Protostar project with cairo 1 support, run 

```shell
protostar init my_project
```

After running the command, the following structure will be generated:

```
my_project/
├── src/
│   ├── business_logic/
│   │   └── utils.cairo
│   ├── contract/
│   │   └── hello_starknet.cairo
│   ├── business_logic.cairo
│   ├── contract.cairo
│   └── lib.cairo
└── Scarb.toml
├── tests/
│   ├── test_hello_starknet.cairo
│   └── test_utils.cairo
└── protostar.toml
```

### `Scarb.toml` and `lib.cairo`

These files define a Cairo package, you can learn more about it [here](./04-understanding-cairo-packages.md).

```toml title="Scarb.toml"
[package]
name = "hello_starknet"
version = "0.1.0"

[dependencies]
```
:::info 
The name of the package is always the value
of the `name` key in the `[package]` section of your `Scarb.toml`. 
:::

### `src`

This directory contains the source code of the package named `hello_starknet`. 

### `contracts`

This directory contains the code of our contract - `HelloStarknet`. As a good practice, we recommend this directory
contains only the contract definition; business logic should be kept in other modules.

:::danger
Currently Protostar only supports having one contract per package. You cannot add more contracts to this directory. To
use multiple contracts in your project, see [this section](#using-multiple-contracts-in-project).
:::

### `business_logic`

This directory contains standalone Cairo 1 methods that can be imported and used in the contract definition. We recommend
putting business logic in this directory to simplify writing unit tests.

### `contract.cairo` and `business_logic.cairo`

These files are necessary so that they can be imported in the `lib.cairo` file.

### `tests`

All [tests](06-testing/README.md) should be defined in this directory.

### `protostar.toml`

This file contains the [configuration for the Protostar project](./05-protostar-toml.md).

```toml title="protostar.toml"
[project]
protostar-version = "0.0.0"

[contracts]
hello_starknet = ["src"]
```

:::info
Even though `hello_starknet.cairo` file is defined in the nested directory, we use a package
directory `src` as a path to the contract. This is necessary for the imports from modules within package
containing the contract (like `business_logic`) to work.
:::

### Minimal project template

If you don't plan to develop a complex project, and you just want to quickly set up the easiest possible one, you can use the `--minimal` flag like this:

```shell
protostar init --minimal my_project
```

This will generate the following file structure:

```
my_project/
├── Scarb.toml
├── protostar.toml
├── src/
│   └── lib.cairo
└── tests/
    └── test_hello_starknet.cairo
```
