---
sidebar_label: protostar.toml V1 (deprecated)
---

# `protostar.toml` V1

:::warning
This version of the configuration file is deprecated.  [Learn how to migrate the configuration file.](/docs/tutorials/project-initialization/protostar-toml-v2#migrating-from-protostartoml-v1)
:::

### Project configuration
```toml title="'protostar.toml' is required"
["protostar.config"]
protostar_version = "0.5.0"

["protostar.project"]
libs_path = "./lib"         

# This section is explained in the "Project compilation" guide.
["protostar.contracts"]
main = [
  "./src/main.cairo",
]

```
### Command configuration

`protostar.toml` can be used to avoid passing arguments every time you run a command. Protostar searches for an argument value in the `["protostar.COMMAND_NAME"]` section, for example:
```toml title="protostar.toml"
# ...

["protostar.build"]
cairo-path = ["./lib/cairo_contracts/src"]
```


If you want to configure a generic argument or an argument that is used by multiple commands (e.g. `cairo-path`), specify it in the `["protostar.shared_command_configs"]` section. This is useful if you want to specify the same `cairo-path` for `build` and `test` commands as demonstrated on the following example:

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