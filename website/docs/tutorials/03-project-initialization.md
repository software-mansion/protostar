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
### Project configuration
Project configuration is required.

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
### Command configuration

Not required arguments can be configured in the `protostar.toml`. It allows you to avoid passing arguments every time you run a command. Protostar checks `["protostar.COMMAND_NAME"]` section and looks for an argument value, for example:
```toml title="protostar.toml"
# ...

["protostar.build"]
cairo-path = ["./lib/cairo_contracts/src"]
```


If you want to configure an argument that is not tied to any command or an argument that is shared across many commands (e.g. `cairo-path`), specify it in the `["protostar.shared_command_configs"]` section. This is useful if you want to specify the same `cairo-path` for `build` and `test` commands as demonstrated on the following example:

```toml title="protostar.toml"
# ...

["protostar.shared_command_configs"]
cairo-path = ["./lib/cairo_contracts/src"]
```

:::info
You can't specify the `profile` argument in the `protostar.toml`.
:::

### Configuration profiles
Configuration profiles provide a way to easily switch between Protostar configurations. This is especially useful for configuring StarkNet networks. Profiles inherit values from non-profiled configuration. In order to create a configuration profile, add a new section in `protostar.toml` with the following naming convention:<br/>  `["profile.PROFILE_NAME.protostar.COMMAND_NAME"]`.

```toml title="protostar.toml"
# ...
["profile.ci.protostar.shared_command_configs"]
no-color = true
```
Then, run Protostar with the `--profile` (or `-p`) argument:
```shell
protostar -p ci ...

```
