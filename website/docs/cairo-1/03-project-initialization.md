---
sidebar_label: Project initialization
---

# Project initialization

## Creating a project

To create a new Protostar project, run 

```shell
protostar init-cairo1 my-project
```

After running the command, the following structure will be generated:

```
my_project/
├── hello_starknet/
│   ├── src/
│   │   ├── business_logic/
│   │   │   └── utils.cairo
│   │   ├── contracts/
│   │   │   └── hello_starknet.cairo
│   │   ├── business_logic.cairo
│   │   ├── contracts.cairo
│   │   └── lib.cairo
│   └── cairo_project.toml
├── tests/
│   ├── test_hello_starknet.cairo
│   └── test_utils.cairo
└── protostar.toml
```

:::warning
This template will be changed in future versions, but the old one will still be usable with newer protostar versions
:::

### `hello_starknet`

This directory contains our only package in this project - `hello_starknet`.

### `cairo_project.toml` and `lib.cairo`

All Cairo1 packages must define these files.

You can learn about [packages](./01-understanding-cairo-packages.md) and how
to [add new module to a package](./01-understanding-cairo-packages.md#adding-a-new-module) in
further sections.

### `contracts`

This directory contains the code of our contract - `HelloStarknet`. As a good practice, we recommend this directory
contains only the contract definition, business logic should be kept in other modules.

:::danger
Currently protostar only supports having one contract per package. You cannot add more contracts to this directory. To
use multiple contracts in your project see [this section](#using-multiple-contracts-in-project).
:::

### `business_logic`

This directory contains standalone cairo1 methods that can be imported and used in the contract definition. We recommend
writing business logic in this directory to simplify writing unit tests.

### `contracts.cairo` and `business_logic.cairo`

These files are necessary so that they can be imported in the `lib.cairo` file.

### `tests`

All [tests](./05-testing.md) should be defined in this directory.

### `protostar.toml`

This file contains the [configuration for the Protostar project](./04-protostar-toml.md).

:::info
Even though `hello_starknet.cairo` file is defined in the nested directory, we use a package
directory `"hello_starknet"` as path to the contract. This is necessary for the imports from modules within package
containing the contract (like `business_logic`) to work.
:::

## Using multiple contracts in project

Due to limitations of the Cairo 1 compiler, having multiple contracts defined in the package will cause
the `protostar build` command and other commands to fail.

**That is, having projects structured like this is not valid and will not work correctly.**

### Multi-contract project structure

Each contract must be defined in the separate package: A different directory with separate `cairo_project.toml`
and `lib.cairo` files defined.

```
my_project/
├── package1/
│   ├── src/
│   │   ├── contracts/
│   │   │   └── hello_starknet.cairo
│   │  ...
│   │   ├── contracts.cairo
│   │   └── lib.cairo
│   └── cairo_project.toml
├── package2/
│   ├── src/
│   │   ├── contracts/
│   │   │   └── other_contract.cairo
│   │  ...
│   │   ├── contracts.cairo
│   │   └── lib.cairo
│   └── cairo_project.toml
...
└── protostar.toml
```

Make sure `[crate_roots]` are correctly defined.

```toml title="package1/cairo_project.toml"
[crate_roots]
package1 = "src"
```

```toml title="package2/cairo_project.toml"
[crate_roots]
package2 = "src"
```

Define each contract in the `[contracts]` section of the protostar.toml and each package
in the `linked-librares`

```toml title="protostar.toml"
# ...
linked-libraries = ["package1", "package2"]

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

For more details on of how to test contracts, see [this page](./04-testing.md).
