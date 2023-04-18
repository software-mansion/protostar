---
sidebar_label: Requirements
---

# Requirements

## Project structure

Projects should follow a defined structure. Learn more in the [project initialization](./02-project-initialization.md)
section.

## Module and crate names

The names must use only ASCII alphanumeric characters or `_`, and cannot be empty. It cannot also start with underscore.
For the alternative reference, please see [this](https://docs.swmansion.com/scarb/docs/reference/manifest#name).

## Multiple contracts for a project

If you wish to have multiple contracts for a single project, you need to put them in
separate [modules](./02-project-initialization.md#using-multiple-contracts-in-project).

## Mutual code for multiple contracts

If you want to have code that will be shared between multiple contracts, you need to wrap this code into a shared
library.
That means you have to wrap this code in the [module](./02-project-initialization.md#cairo-1-modules) and then add a
path of this module to the [protostar.toml](./02-project-initialization.md#the-protostartoml)'s `linked-libraries`.
