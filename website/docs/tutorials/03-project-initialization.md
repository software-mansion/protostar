---
sidebar_label: Project initialization
---

# Project initialization

To create a new Protostar project, you will need to run the `protostar init` command followed by the name of your project. For example:

```console
protostar init your-project-name
```

This will create a new directory with the specified name, generate a [configuration file named `protostar.toml`](/docs/tutorials/configuration-file), and create example contract and test files in the `src` and `tests` directories, respectively.

The resulting project structure will be as follows:
```
your-project-name/
├── src/
│   └── main.cairo
├── tests/
│   └── test_main.cairo
└── protostar.toml
```

The example contract file, `main.cairo`, and the example test file, `test_main.cairo`, serve as templates for your project.

The configuration file, `protostar.toml`, defines the root directory of your Protostar project.

### Adapting an existing project to a Protostar project
If you already have an existing project that you want to adapt to a Protostar project, you can do so by adding a valid `protostar.toml` configuration file to the root of the project.

Alternatively, you can use the `protostar init --existing` command to create a `protostar.toml` in your existing project.
This command will create the `protostar.toml` file in the current directory, which should be the root of your existing project.


