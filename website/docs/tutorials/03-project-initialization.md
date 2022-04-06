---
sidebar_label: Project initialization (1 min)
---

# Project initialization

To create a new project run:

```console
protostar init
```

```console title="Protostar configuration step."
libraries directory name (lib):
```

# Project structure

The result of running `protostar init` is a configuration file `protostar.toml`, example files, and the following 3 directories:

- `src` — A directory for your code.
- `lib` — A default directory for an external dependencies.
- `tests` — A directory storing tests.

## `protostar.toml`

```toml
["protostar.config"]
protostar_version = "0.1.0"

["protostar.project"]
libs_path = "./lib"         # a path to the dependency directory

# This section is explained in the "Project compilation" guide.
["protostar.contracts"]
main = [
  "./src/main.cairo",
]

```
