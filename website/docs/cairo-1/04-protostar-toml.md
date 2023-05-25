# Understanding protostar.toml

Protostar can be configured with file `protostar.toml`, which is located in the root of your project. The file uses
the [TOML](https://toml.io/en/) format and allows you to specify various options and settings for Protostar.

Here is an example `protostar.toml` file:

```toml title="protostar.toml example"
[project]
protostar-version = "PROTOSTAR_VERSION"

# Shared Configuration (affects all commands)
linked-libraries = ["hello_starknet"]

# Defines contract names for the use with cheatcodes and commands
[contracts]
hello_starknet = ["hello_starknet"]

# Per command configuration profile
[profile.integration.test]
target = ["tests/integration"]
report-slowest-tests = 5

# Shared configration profile
[profile.devnet.project]
gateway-url = "http://127.0.0.1:5050/"
chain-id = 1536727068981429685321

[profile.testnet.project]
network = "testnet"
```

### `[project]` section

The `[project]` section of the `protostar.toml` file allows you to specify global options and settings for your project.

#### `protostar-version`

This attribute defines which Protostar version should be used with your project.

#### `linked-libraries`

It defines packages to be used when running tests and other commands. If a package is not included in `linked-libraries`
trying to use it in tests will cause compilation errors.

### `[contracts]` section

Define packages containing contracts to be used by protostar commands
like [declare](../cli-reference.md#declare) and by [cheatcodes](./05-testing/03-cheatcodes.md).

```toml
[contracts]
my_contract = ["my_contract"]
other_contract = ["other_contract"]
```

### Command Arguments Configuration Section

This section of the `protostar.toml` file allows you to specify arguments for a specific
Protostar command.


For example, you can define a different build dir for the [build](../cli-reference.md#build)

```toml title="Configuration File"
[build]
compiled-contracts-dir = "my_dir"
```

These arguments will be automatically used when running a command.

### Configuration Profiles

Configuration profiles allow you to easily switch between different Protostar configurations.
When you use a profile, it will override the default settings specified in the `protostar.toml` file with the settings
specified in the profile.

To create a configuration profile, add a new section to the `protostar.toml`. For example:

- to create a configuration named `mainnet` for the [`declare` command](../cli-reference.md#declare),
  add `[profile.mainnet.declare]` section
- to create a shared configuration named `testnet`, add `[profile.testnet.project]` section

To use a profile, add the [-p or --profile argument](../cli-reference.md#-p---profile-string) followed by the name of
the profile.
For example, to use the [`declare` command](../cli-reference.md#declare) with the `testnet` profile,
run:

```console
protostar -p testnet declare
```