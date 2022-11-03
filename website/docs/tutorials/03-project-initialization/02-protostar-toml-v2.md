---
sidebar_label: protostar.toml V2
---
# `protostar.toml` V2

```toml title="protostar.toml example"
[project]
protostar-version = "PROTOSTAR_VERSION"     # required

# Shared Configuration (affects all commands)
lib-path = "lib"                            # install, update, remove
cairo-path = ["lib/cairo-contracts/src"]    # build, test

# Defines contract names. Currently, this section is required by the build command.
[contracts]
main = ["src/feature_a.cairo", "src/feature_b.cairo"]   
proxy = ["src/proxy.cairo"]
account = ["src/account.cairo"]

# Command Configuration
[test]
target = ["src"]

# Command Configuration Profile
[profile.integration.test]
target = ["tests/integration"]
report-slowest-tests = 5

# Shared Configuration Profile
[profile.devnet.project]
gateway-url = "http://127.0.0.1:5050/"
chain-id = 1536727068981429685321

[profile.testnet.project]
network = "testnet"
```


### `[project]`
#### `protostar-version`
This attribute is used to warn you about compatibility issues between Protostar and a project.

#### Shared Configuration
You can keep command arguments in the `[project]` to share them across commands. Read the [`[COMMAND]` section](#command) to learn how to configure command arguments in the configuration file.

### `[contracts]`
This section allows you to refer to a contract by a contract name across Protostar features. Decoupling contract names from file paths makes the code:
- easier to maintain — e.g. changes to folder or file names don't break your tests
- easier to read — the code is more focused
- easier to write — removes the need of mental mapping

:::note
Currently, [`protostar build`](/docs/cli-reference#build) requires this section.
:::

### `[COMMAND]`
Configure command arguments, to avoid passing them manually. CLI can be represented in the configuration file in the following way:

```console title="CLI"
protostar format src tests --ignore-broken
```
```toml title="Configuration File"
[format]
target = ["src", "tests"]
ignore-broken = true
```

Check the [CLI Reference](/docs/cli-reference) or run `protostar COMMAND --help` to learn supported arguments.

Specify arguments in the [`[project]` section](#shared-configuration) to share configuration across commands.



### Configuration Profiles
Configuration profiles provide a way to easily switch between Protostar configurations. Profiles inherit values from non-profiled configuration. In order to create a configuration profile, add a new section in protostar.toml with the following naming convention:
-  `[profile.PROFILE_NAME.project]` - to create a profile for a [Shared Configuration](#shared-configuration)
-  `[profile.PROFILE_NAME.COMMAND]` - to create a profile for a [Command Configuration](#command)

To activate the profile, use the profile argument
```console title="Run the test command with the 'integration' profile"
protostar -p integration test
```

## Migrating from `protostar.toml` V1
In order to migrate your protostar.toml V1, run:
```
protostar migrate-configuration-file
```


### Changes
- removed `protostar` prefix from configuration sections
- section names cannot be in double quotes
- merged `["protostar.config"]` and `["protostar.shared_command_configs"]` sections into the project section
- `snake_case` is no longer supported (use `kebab-case` everywhere)


| protostar.toml V1                                    | protostar.toml V2            |
| ---------------------------------------------------- | ---------------------------- |
| `["protostar.config"]`                               | `[project]`                  |
| `["protostar.project"]`                              | `[project]`                  |
| `["protostar.shared_command_configs"]`               | `[project]`                  |
| `["protostar.contracts"]`, `["protostar.<COMMAND>"]` | `[contracts]`, `[<COMMAND>]` |
| `cairo_path = ...`, `cairo-path = ...`               | `cairo-path = ...`           |

