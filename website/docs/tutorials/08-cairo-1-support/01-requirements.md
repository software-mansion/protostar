---
sidebar_label: Requirements
---

# Requirements

## Project structure

Projects should follow a defined structure. Learn more in the [project initialization](./02-project-initialization.md)
section.

## Multiple contracts in a single project

If you wish to have multiple contracts for a single project, you need to put them in
separate [packages](./02-project-initialization.md#cairo-1-packages). You can learn more about
packages [here](./02-project-initialization.md#cairo-1-packages).

### Setting up multiple modules

Having multiple packages requires some considerations. Learn more about
it [here](./02-project-initialization.md#using-multiple-contracts-in-project).

### Module and package names

The names must use only ASCII alphanumeric characters or `_`, and cannot be empty. It cannot also start with underscore.
For the alternative reference, please see [this](https://docs.swmansion.com/scarb/docs/reference/manifest#name).

### Sharing common code

If you want to have code that will be shared between multiple contracts, you need to wrap this code into
a [package](./02-project-initialization.md#cairo-1-packages) and then add a
path of this package to the [protostar.toml](./02-project-initialization.md#the-protostartoml)'s `linked-libraries`.
