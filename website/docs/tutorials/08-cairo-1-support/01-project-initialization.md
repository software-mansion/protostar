---
sidebar_label: Project initialization
---

# Project initialization

## Creating a project
To create a new Protostar project with cairo1 support, you will need to run the `protostar init-cairo1` command followed by the name of your project.

After running the command, the following structure will be generated:

```
./your-project-name
|-- protostar.toml
|-- src
|   |-- cairo_project.toml
|   |-- lib.cairo
|   `-- main.cairo
`-- tests
    `-- test_main.cairo
```

This template contains:

- `src` directory
    - `cairo_project.toml` which is needed for compilation 
    - `main.cairo` file with one function definition
    - `lib.cairo` file which defines the module
- `test` directory
    - Single test file with one test for function defined in `main.cairo`
- `protostar.toml` containing information about the project

## The protostar.toml
Apart from the usual things you find in `protostar.toml`, there is `linked-libarires` entry which is used to find cairo 1 modules in tests and building.
This makes it possible for you to include other modules from your dependencies, if they are correct cairo 1 modules (with their own module definition and `cairo_project.toml`).

```
[project]
protostar-version = "0.9.2"
lib-path = "lib"
linked-libraries = ["src"]

[contracts]
```

:::warning
`[contracts]` section is not usable right now, since protostar can't build cairo 1 contracts yet 
:::