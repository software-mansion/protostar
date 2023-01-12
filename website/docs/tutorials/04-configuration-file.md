# Configuration file
Protostar can be configured with file `protostar.toml`, which is located in the root of your project. The file uses the [TOML](https://toml.io/en/) format and allows you to specify various options and settings for Protostar.

Here is an example `protostar.toml` file:


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
The `[project]` section of the `protostar.toml` file allows you to specify global options and settings for your project.
#### `protostar-version`
This attribute is defines what Protostar version should be used with your project.
It should be set to the latest compatible Protostar version.
If you try to use a different version of Protostar with your project, you will receive a warning and you may experience unexpected errors.
This attribute should be updated manually.

#### Shared Configuration
You can specify options that are shared by multiple Protostar commands in the `[project]` section.
For example, the [`lib-path`](/docs/cli-reference#--lib-path-path) option is used by the [`install`](/docs/cli-reference#install), [`update`](/docs/cli-reference#update), and [`remove`](/docs/cli-reference#remove) commands, and [`cairo-path`](/docs/cli-reference#--cairo-path-path) is used by the [`build`](/docs/cli-reference#build) and [`test`](/docs/cli-reference#test) commands.

### `[contracts]`
The `[contracts]` section allows you to define contract names and the corresponding files that make up each contract.
This is useful because it allows you to refer to contracts by name rather than having to specify the full file path each time.
You can also combine multiple files into a single contract.
Currently, the `[contracts]` section is required by the [`protostar build`](/docs/cli-reference#build) command.

Here is an example of how to define a contract in the [contracts] section:

```toml
[contracts]
my_contract = ["src/feature_a.cairo", "src/feature_b.cairo"]   
```

### `[COMMAND]`
The `[COMMAND]` section of the `protostar.toml` file allows you to specify options and settings for a specific Protostar command.

To configure command arguments in the `protostar.toml` file, you can specify them in a `[COMMAND]` section using the following format:

```toml
[COMMAND]
flag = true
list = [1, 2, 3]
path = "./src"
```

For example, the following configuration file specifies the [`target`](/docs/cli-reference#target-string) and [`ignore-broken`](/docs/cli-reference#--ignore-broken) arguments for the [`protostar format` command](/docs/cli-reference#format):

```toml title="Configuration File"
[format]
target = ["src", "tests"]
ignore-broken = true
```

You can then run the [`protostar format`](/docs/cli-reference#format) command without specifying the [`target`](/docs/cli-reference#target-string) and [`ignore-broken`](/docs/cli-reference#--ignore-broken) arguments in the console:

```console title="CLI"
protostar format
```

To learn more about the available options and arguments for each Protostar command, refer to the [CLI Reference](/docs/cli-reference) or run `protostar COMMAND --help` to see the list of supported arguments.

### Configuration Profiles
Configuration profiles allow you to easily switch between different Protostar configurations. 
When you use a profile, it will override the default settings specified in the `protostar.toml` file with the settings specified in the profile.

To create a configuration profile, add a new section to the `protostar.toml` file with the following naming convention:
-  `[profile.PROFILE_NAME.project]` - to create a [Shared Configuration](#shared-configuration) profile
-  `[profile.PROFILE_NAME.COMMAND]` - to create a [Command Configuration](#command) profile

To use a profile, specify the [-p or --profile argument](/docs/cli-reference#-p---profile-string) followed by the name of the profile:

```console
protostar -p PROFILE_NAME COMMAND
```

For example, to use the [`test` command](/docs/cli-reference#test) with the `smoke_tests` profile, run:
```console title="Run the test command with the 'integration' profile"
protostar -p smoke_tests test
```

## Migrating from an Older Version of `protostar.toml`
If you have a `protostar.toml` file created by an older version of Protostar, you can use the [`protostar migrate-configuration-file` command](/docs/cli-reference#migrate-configuration-file) to update it to the latest format.

This command makes the following changes to your protostar.toml file:

- Removes the `protostar` prefix from configuration sections
- Changes section names to not be in double quotes
- Merges the `["protostar.config"]` and `["protostar.shared_command_configs"]` sections into the `[project]` section
- Changes all keys to use `kebab-case` instead of `snake_case`

Here is a table showing the changes between the old and new configuration files:

| protostar.toml V1                                  | protostar.toml V2          |
| -------------------------------------------------- | -------------------------- |
| `["protostar.config"]`                             | `[project]`                |
| `["protostar.project"]`                            | `[project]`                |
| `["protostar.shared_command_configs"]`             | `[project]`                |
| `["protostar.contracts"]`, `["protostar.COMMAND"]` | `[contracts]`, `[COMMAND]` |
| `cairo_path = ...`, `cairo-path = ...`             | `cairo-path = ...`         |

To migrate your protostar.toml file, run the following command:

```console
protostar migrate-configuration-file
```