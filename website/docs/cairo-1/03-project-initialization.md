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
│   ├── contracts/
│   │   └── hello_starknet.cairo
│   ├── business_logic.cairo
│   ├── contracts.cairo
│   └── lib.cairo
└── Scarb.toml
├── tests/
│   ├── test_hello_starknet.cairo
│   └── test_utils.cairo
└── protostar.toml
```

### `Scarb.toml` and `lib.cairo`

All Cairo 1 packages must define these files.

You can learn about [packages](./02-understanding-cairo-packages.md) and how
to [add new module to a package](./02-understanding-cairo-packages.md#adding-a-new-module) in
further sections.

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
contains only the contract definition, business logic should be kept in other modules.

:::danger
Currently protostar only supports having one contract per package. You cannot add more contracts to this directory. To
use multiple contracts in your project see [this section](#using-multiple-contracts-in-project).
:::

### `business_logic`

This directory contains standalone Cairo 1 methods that can be imported and used in the contract definition. We recommend
putting business logic in this directory to simplify writing unit tests.

### `contracts.cairo` and `business_logic.cairo`

These files are necessary so that they can be imported in the `lib.cairo` file.

### `tests`

All [tests](06-testing/README.md) should be defined in this directory.

### `protostar.toml`

This file contains the [configuration for the Protostar project](./04-protostar-toml.md).

```toml title="protostar.toml"
[project]
protostar-version = "0.0.0"
lib-path = "lib"

[contracts]
hello_starknet = ["src"]
```

:::info
Even though `hello_starknet.cairo` file is defined in the nested directory, we use a package
directory `src` as path to the contract. This is necessary for the imports from modules within package
containing the contract (like `business_logic`) to work.
:::

## Using multiple contracts in project

Due to limitations of the Cairo 1 compiler, having multiple contracts defined in the package will cause
the `protostar build` command and other commands to fail.

**That is, having projects structured like this is not valid and will not work correctly.**

### Multi-contract project structure

Each contract must be defined in the separate package: a different directory with separate `Scarb.toml`
and `src/lib.cairo` files defined.

```
my_project/
├── package1/
│   ├── src/
│   │   ├── contracts/
│   │   │   └── hello_starknet.cairo
│   │  ...
│   │   ├── contracts.cairo
│   │   └── lib.cairo
│   └── Scarb.toml
├── package2/
│   ├── src/
│   │   ├── contracts/
│   │   │   └── other_contract.cairo
│   │  ...
│   │   ├── contracts.cairo
│   │   └── lib.cairo
│   └── Scarb.toml
...
├── src/
│   └── lib.cairo
├── Scarb.toml
└── protostar.toml
```

Notice that the whole project itself is a package too.
This is due to the fact that [Scarb](https://docs.swmansion.com/scarb/), which Protostar uses 
to manage dependencies, does not support workspaces yet. If you do not
need to include any code in the top level package, just leave the `my_project/src/lib.cairo` file empty.

:::info 
Even though `package1` and `package2` **directories** are inside `my_project` **directory**
it does not make `package1` and `package2` **packages** parts of `my_project` **package**. 
Therefore, you should refer to them using `package1::` and `package2::`.
:::

Define each contract in the `[contracts]` section of the protostar.toml.
```toml title="protostar.toml"
# ...
[contracts]
hello_starknet = ["package1"]
other_contract = ["package2"]
```

### Testing multi-contract projects

For example, to test function `returns_two` defined in the `package1/business_logic/utils.cairo` write

```cairo title="Example test"
#[test]
fn test_returns_two() {
    assert(package1::business_logic::utils::returns_two() == 2, 'Should return 2');
}
```

Or using the `use path:to::mod` syntax

```cairo title="Example test
use package1::business_logic::utils::returns_two;

#[test]
fn test_returns_two() {
    assert(returns_two() == 2, 'Should return 2');
}
```

Make sure that the path::to:the::module is correct for your package structure.

For more details on of how to test contracts, see [this page](06-testing/README.md).
