---
sidebar_label: Requirements
---

# Requirements

## Project structure

:::note
Cairo 1 is constantly being updated, so all the requirements mentioned here may change in the future.
:::

Currently, Cairo1 forces the following file structure of a contract:
```
my-contract/
├── lib.cairo
├── cairo_project.toml
```

That means that you can have only one contract per module. More information about modules [here](./02-project-initialization.md#cairo-1-modules).

- `my_contract` - a root directory for a contract
    - `cairo_project.toml` which is needed for compilation. Its purpose is to specify a path to the crate roots of the contract.
    This file usually looks like this:
    ```
    [crate_roots]
    my_contract = "."
    ```
    - `lib.cairo` file which defines the module and may also contain the code of the contract.

## Multiple contracts for a project

If you wish to have multiple contracts for a single project, you need to put them in separate [modules](./02-project-initialization.md#cairo-1-modules).

## Mutual code for multiple contracts

If you want to have code that will be shared between multiple contracts, you need to wrap this code into a shared library.
That means you have to wrap this code in the [module](./02-project-initialization.md#cairo-1-modules) and then add a path of this module to the [protostar.toml](./02-project-initialization.md#the-protostartoml)'s `linked-libraries`.
