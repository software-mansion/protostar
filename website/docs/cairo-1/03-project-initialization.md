---
sidebar_label: Project initialization
---

# Project initialization

## Creating a project

To create a new Protostar project with Cairo 1 support, run 

```shell
protostar init my_project
```

This will create a new directory with the specified name, generate
[protostar.toml](05-protostar-toml.md) and [Scarb.toml](04-understanding-cairo-packages.md#dependencies-management)
configuration files, and create an example [multimodule](04-understanding-cairo-packages.md#modules) project containing 
two [test](06-testing/README.md) files and a [package](04-understanding-cairo-packages.md#packages) with a contract.

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
