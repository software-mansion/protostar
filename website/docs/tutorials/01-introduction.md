---
sidebar_label: Introduction (1 min)
---

# Introduction

Protostar is a StarkNet smart contract development [toolchain](https://en.wikipedia.org/wiki/Toolchain), which helps you with the following tasks:

- [dependencies management](/docs/tutorials/guides/dependencies-management)
- [project compilation](/docs/tutorials/guides/compiling)
- [testing contracts](/docs/tutorials/guides/testing)

:::note
Protostar takes its inspiration from [Foundry](https://onbjerg.github.io/foundry-book/index.html).
:::

## Target audience

This guides assume you have basic knowledge about [Cairo and StarkNet](https://www.cairo-lang.org/docs/) and Git.

## Learning objectives

After reading this guides, you will know how to do the following:

- [install and upgrade Protostar](/docs/tutorials/installation)
- [initialize a new Protostar project](/docs/tutorials/project-initialization)
- [configure `protostar.toml`](/docs/tutorials/project-initialization#protostartoml)
- [adapt an existing Cairo project to the Protostar project](/docs/tutorials/project-initialization#adapting-an-existing-project-to-the-protostar-project)
- [compile project](/docs/tutorials/guides/compiling)
- [add, update, and remove dependencies](/docs/tutorials/guides/dependencies-management)
- [test contracts with the help of cheatcodes](/docs/tutorials/guides/testing)
- [deploy contracts using Protostar](/docs/tutorials/guides/deployment)

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
