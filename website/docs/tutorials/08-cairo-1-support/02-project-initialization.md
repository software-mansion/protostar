---
sidebar_label: Project initialization
---

# Project initialization

## Creating a project

To create a new Protostar project with cairo 1.0 support, you will need to run the `protostar init-cairo1` command followed
by the name of your project. For example:

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

This directory contains our only module in this project - `hello_starknet`.

### `cairo_project.toml` and `lib.cairo`

All Cairo1 crates must define these files.

- `cairo_project.toml` - this file defines the name of the crate. It is good practice for this name to match the
  top-level directory name - `hello_starknet` in our case.
- `lib.cairo` - this file exposes all of our modules to the compiler. Initially, it only contains two modules:

```cairo title="lib.cairo"
mod business_logic;
mod contracts;
```

You can learn about [modules](#cairo-1-modules) and [how to add them](#adding-a-new-module) in further sections.

### `contracts`

This directory contains the code of our contract - `HelloStarknet`. As a good practice, we recommend this directory
contains
only the contract definition, bussines logic should be kept in other modules.

:::danger
Currently protostar only supports having one contract per module. You cannot add more contracts to this directory. To
use multiple contracts in your project see [this section](#using-multiple-contracts-in-project).
:::

### `business_logic`

This directory contains standalone cairo1 methods that can be imported and used in the contract definition. We recommend
writing business logic in this directory for ease of writing unit tests.

### `contracts.cairo` and `business_logic.cairo`

`contracts.cairo` and `business_logic.cairo`: All modules must be listed in `lib.cairo`
Note that these files only contain `mod ...` definitions that import files from directories.

Creation of these files is necessary so that they can be imported in the `lib.cairo file`.

```cairo title="contracts.cairo
mod hello_starknet;
```

### `tests`

All tests should be defined in this directory.

### `protostar.toml`

This file contains the configuration for the Protostar project.

## Cairo 1 modules

In order to understand how to create Cairo 1.0 modules, we need to talk about the purpose of `cairo_project.toml`
and `lib.cairo`.

### Project defaults

#### 1. `cairo_project.toml`

It is needed for the definition of crate roots, which are the places where `lib.cairo` files are located.

The default `cairo_project.toml` file contains only the definition of the `my_project` crate which is contained in
the `src` directory.

```toml
[crate_roots]
my_project = "src"
```

#### 2. `lib.cairo`

It is the root of the module tree of the package. Here you can define functions, declare used modules, etc.

The default one has `contracts` and `business_logic` modules declarations:

```
mod business_logic;
mod contracts;
```

### Creating and using a new modules

Suppose we wanted to create a module called `mod1` inside the `src` crate and use it in tests.
We want this module to only have one file `functions.cairo` containing one function defined like:

```cairo
fn returns_three() -> felt252 {
    3
}
```

#### Adding a new module

Here are the steps we need to take:

1. Create a `mod1` directory in the `src` crate
2. Create file `functions.cairo` inside `mod1` and define your code there
3. Create `mod1.cairo` file **in the `src` crate**, with the contents of

```cairo
mod functions;
```

4. Update the `lib.cairo` file to include `mod1`. It's contents should now look like this

```cairo
// previous code stays
// ...
mod mod1;
```

If you followed the steps correctly, your new project structure should look like this

```
my_project/
├── hello_starknet/
│   ├── src/
│   │   ├── business_logic/
│   │   │   └── utils.cairo
│   │   ├── contracts/
│   │   │   └── hello_starknet.cairo
│   │   ├── mod1/  <------------------- new directory
│   │   │   └── functions.cairo  <----- new file
│   │   ├── business_logic.cairo
│   │   ├── contracts.cairo
│   │   ├── lib.cairo  <--------------- contents updated
│   │   └── mod1.cairo  <-------------- new file
│   └── cairo_project.toml
├── tests/
│   ├── test_hello_starknet.cairo
│   └── test_utils.cairo
└── protostar.toml
```

#### Using added module

You now use your function in the HelloStarknet contract use `my_project::mod1::functions::returns_three()`.

## The protostar.toml

Apart from the usual things you can find in `protostar.toml`, there is a `linked-libarires` entry which is used to find
cairo1 modules in tests and building.
This makes it possible for you to include other modules from your dependencies if they are correct cairo1 modules (with
their own module definition and `cairo_project.toml`).

```
[project]
protostar-version = "0.9.2"
lib-path = "lib"
linked-libraries = ["hello_starknet"]

[contracts]
hello_starknet = ["hello_starknet"]
```

:::info
Even though `hello_starknet.cairo` file is defined in the nested directory, we use `"src"` as path to the contract. This
is necessary for the imports from other modules (like `business_logic`) to work.
:::

## Using multiple contracts in project

Due to limitations of cairo1 compiler, having multiple contracts defined in the project will cause `protostar build` and
other commands to fail.

**That is, having projects structured like this is not valid and will not work correctly.**

### ❌ Incorrect multi-contract project structure

Multi-contract projects structure like this will not work:

```
my_project/
├── hello_starknet/
│   ├── src/
│   │  ...
│   │   ├── contracts/
│   │   │   ├── hello_starknet.cairo
│   │   │   └── other_contract.cairo
│   │  ...
│   └── cairo_project.toml
... ...
└── protostar.toml
```

```cairo title="hello_starknet.cairo"
#[contract]
mod HelloStarknet {
    // ...
}
```

```cairo title="other_contract.cairo"
#[contract]
mod HelloStarknet {
    // ...
}
```

### ✅ Correct multi-contract project structure

Instead, each contract must be defined in the separate crate: A different directory with separate `cairo_project.toml`
and
`lib.cairo` files defined.

```
my_project/
├── hello_starknet/
│   ├── src/
│   │   ├── contracts/
│   │   │   └── hello_starknet.cairo
│   │  ...
│   │   ├── contracts.cairo
│   │   └── lib.cairo
│   └── cairo_project.toml
├── other_contract/
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

```toml title="crate1/cairo_project.toml"
[crate_roots]
crate1 = "src"
```

```toml title="crate2/cairo_project.toml"
[crate_roots]
crate2 = "src"
```

Define each contract in the `[contracts]` section of the protostar.toml and crates
in the `linked-librares`

```toml title="protostar.toml"
# ...
linked-libraries = ["crate1", "crate2"]

[contracts]
hello_starknet = ["crate1"]
other_contract = ["crate2"]
```

### Testing multi-contract projects

You can write your tests in the standard manner. Make sure you use correct paths.
For example, to test function `returns_two` defined in the `crate1/business_logic/utils.cairo` write

```cairo title="Example test"
#[test]
fn test_returns_two() {
    assert(crate1::business_logic::utils::returns_two() == 2, 'Should return 2');
}
```

### Modules names considerations

The names must use only ASCII alphanumeric characters or `_`, and cannot be empty. It cannot also start with underscore.