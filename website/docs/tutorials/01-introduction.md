---
sidebar_label: Introduction
---

# Introduction

Protostar is a StarkNet smart contract development [toolchain](https://en.wikipedia.org/wiki/Toolchain), which helps you with the following tasks:

- [dependencies management](06-dependencies-management.md)
- [project compilation](05-compiling.md)
- [testing contracts](07-testing/README.md)

:::note
Protostar takes its inspiration from [Foundry](https://github.com/foundry-rs/foundry).
:::

## Target audience

This guides assume you have basic knowledge about [Cairo and StarkNet](https://www.cairo-lang.org/docs/) and Git.

## Learning objectives

After reading this guides, you will know how to do the following:

- [install and upgrade Protostar](02-installation.md)
- [initialize a new Protostar project](03-project-initialization.md)
- [configure `protostar.toml`](03-project-initialization.md#protostartoml)
- [adapt an existing Cairo project to the Protostar project](03-project-initialization.md#adapting-an-existing-project-to-the-protostar-project)
- [compile project](05-compiling.md)
- [add, update, and remove dependencies](06-dependencies-management.md)
- [test contracts with the help of cheatcodes](07-testing/README.md)
- [interacting with StarkNet (calling, invoking, deploying contracts)](08-interacting-with-starknet/README.md)

## Reference
Protostar is designed to be discoverable straight from the terminal. If you want to get the information about available commands and flags, you can always use:
```
protostar --help
```
If you want to get the detailed information about a certain command and available flags, you can always use:
```
protostar COMMAND --help
```
For example, `protostar test --help`.
