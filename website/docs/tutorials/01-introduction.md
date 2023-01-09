---
sidebar_label: Introduction
---

# Introduction

Protostar is a toolchain for developing StarkNet smart contracts that helps with tasks such as [dependencies management](06-dependencies-management.md), [project compilation](05-compiling.md), and [testing contracts](07-testing/README.md).
It is inspired by [Foundry](https://github.com/foundry-rs/foundry).

## Target audience
These guides assume that you have basic knowledge of [Cairo, StarkNet](https://www.cairo-lang.org/docs/), and Git.

## Learning objectives

After reading these guides, you will know how to:
- [Install and upgrade Protostar](02-installation.md)
- [Initialize a new Protostar project](03-project-initialization.md)
- [Configure `protostar.toml`](03-project-initialization.md#protostartoml)
- [Adapt an existing StarkNet project to the Protostar project](03-project-initialization.md#adapting-an-existing-project-to-the-protostar-project)
- [Compile project](05-compiling.md)
- [Add, update, and remove dependencies](06-dependencies-management.md)
- [Test contracts using cheatcodes](07-testing/README.md)
- [Interact with StarkNet (call, invoke, deploy contracts)](08-interacting-with-starknet/README.md)

## Reference
Protostar is designed to be easily discoverable from the terminal.
To view information about available commands and flags, run:
```
protostar --help
```
For detailed information about a specific command and its flags, run:
```
protostar COMMAND --help
```
For example, `protostar test --help`.
