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

### Adapting an existing project to the Protostar project
Protostar project must be a git repository and have `protostar.toml` file. You can adapt your project manually or by running `protostar init --existing`.

# Project structure

The result of running `protostar init` is a configuration file `protostar.toml`, example files, and the following 3 directories:

- `src` — A directory for your code.
- `lib` — A default directory for an external dependencies.
- `tests` — A directory storing tests.

## `protostar.toml`

```toml title="protostar.toml"
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
Protostar's commands can be configured in the `protostar.toml`. This is number of arguments you would have to provide in the CLI otherwise. Protostar expects a section `["protostar.COMMAND_NAME"]` and a argument name with underscores (`_`) in place of dashes (`-`), for example:
```toml title="protostar.toml"
# ...

["protostar.build"]
cairo_path = ["./lib/cairo_contracts/src"]
```

If you want configure an argument that is not tied to any command or an argument that is shared across many commands (e.g. `cairo-path`), specify configuration in the `["protostar.shared_command_configs"]` section. This is useful if you want to specify the same `cairo-path` for `build` and `test` commands as demonstrated on the following example:

```toml title="protostar.toml"
# ...

["protostar.shared_command_configs"]
cairo_path = ["./lib/cairo_contracts/src"]
```