# CLI Reference
## Common flags
#### `--no-color`
Disable colors.
#### `-p` `--profile STRING`
Specifies active profile configuration. This argument can't be configured in `protostar.toml`.
#### CI configuration
```toml title="protostar.toml"
[profile.ci.protostar.shared_command_configs]
no_color=true
```
`protostar -p ci test`

#### Deployment configuration
```toml title="protostar.toml"
[profile.devnet.protostar.deploy]
gateway_url="http://127.0.0.1:5050/"
```
`protostar -p devnet deploy ...`
#### `-v` `--version`
Show Protostar and Cairo-lang version.
## Commands
### `build`
```shell
$ protostar build
```
Compile contracts.
#### `--cairo-path DIRECTORY[]`
Additional directories to look for sources.
#### `--disable-hint-validation`
Disable validation of hints when building the contracts.
#### `-o` `--output PATH=build`
An output directory used to put the compiled contracts in.
### `declare`
Sends a declare transaction to StarkNet.
#### `contract PATH`
Required.

Path to compiled contract.
#### `--gateway-url STRING`
The URL of a StarkNet gateway. It is required unless `--network` is provided.
#### `-n` `--network STRING`
The name of the StarkNet network.
It is required unless `--gateway-url` is provided.

Supported StarkNet networks:
- `alpha-goerli`
- `alpha-mainnet`
#### `--signature INT[]`
Signature information for the declaration.
#### `--token STRING`
Used for declaring contracts in Alpha MainNet.
#### `--wait-for-acceptance`
Waits for transaction to be accepted on chain.
### `deploy`
```shell
protostar deploy ./build/main.json --network alpha-goerli
```
Deploys contracts.
#### `contract PATH`
Required.

The path to the compiled contract.
#### `--gateway-url STRING`
The URL of a StarkNet gateway. It is required unless `--network` is provided.
#### `-i` `--inputs INT[]`
The inputs to the constructor. Calldata arguments may be of any type that does not contain pointers.
[Read more about representing Cairo data types in the CLI.](https://www.cairo-lang.org/docs/hello_starknet/more_features.html#array-arguments-in-calldata)
#### `-n` `--network STRING`
The name of the StarkNet network.
It is required unless `--gateway-url` is provided.

Supported StarkNet networks:
- `alpha-goerli`
- `alpha-mainnet`
#### `--salt INT`
An optional salt controlling where the contract will be deployed. The contract deployment address is determined by the hash of contract, salt and caller. If the salt is not supplied, the contract will be deployed with a random salt.
#### `--token STRING`
Used for deploying contracts in Alpha MainNet.
#### `--wait-for-acceptance`
Waits for transaction to be accepted on chain.
### `init`
```shell
$ protostar init
```
Create a Protostar project.
#### `--existing`
Adapt current directory to a Protostar project.
### `install`
```shell
$ protostar install https://github.com/OpenZeppelin/cairo-contracts
```
Install a dependency as a git submodule.
#### `package STRING`
- `GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]`
    - `OpenZeppelin/cairo-contracts@0.1.0`
- `URL_TO_THE_REPOSITORY`
    - `https://github.com/OpenZeppelin/cairo-contracts`
- `SSH_URI`
    - `git@github.com:OpenZeppelin/cairo-contracts.git`

#### `--name STRING`
A custom package name. Use it to resolve name conflicts.
### `migrate`
Run migration file.
#### `path PATH`
Required.

Path to the migration file.
#### `--gateway-url STRING`
The URL of a StarkNet gateway. It is required unless `--network` is provided.
#### `-n` `--network STRING`
The name of the StarkNet network.
It is required unless `--gateway-url` is provided.

Supported StarkNet networks:
- `alpha-goerli`
- `alpha-mainnet`
#### `--no-confirm`
Skip confirming building the project.
#### `--output-dir PATH`
Migration output directory.
#### `--rollback`
Run `rollback` function in the migration script.
### `remove`
```shell
$ protostar remove cairo-contracts
```
Remove a dependency.
#### `package STRING`
Required.

- `GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]`
    - `OpenZeppelin/cairo-contracts@0.1.0`
- `URL_TO_THE_REPOSITORY`
    - `https://github.com/OpenZeppelin/cairo-contracts`
- `SSH_URI`
    - `git@github.com:OpenZeppelin/cairo-contracts.git`
- `PACKAGE_DIRECTORY_NAME`
    - `cairo_contracts`, if the package location is `lib/cairo_contracts`
### `test`
```shell
$ protostar test
```
Execute tests.
#### `target STRING[]=['tests']`
A glob or globs to a directory or a test suite, for example:
- `tests/**/*_main*::*_balance` — find test cases, which names ends with `_balance` in test suites with the `_main` in filenames in the `tests` directory
- `::test_increase_balance` — find `test_increase_balance` test_cases in any test suite within the project 

#### `--cairo-path DIRECTORY[]`
Additional directories to look for sources.
#### `--disable-hint-validation`
Disable hint validation in contracts declared by the `declare` cheatcode or deployed by `deploy_contract` cheatcode.

#### `-x` `--exit-first`
Exit immediately on first broken or failed test
#### `--fuzz-max-examples INT=100`
Once this many satisfying examples have been considered without finding any counter-example, falsification will terminate.
#### `-i` `--ignore STRING[]`
A glob or globs to a directory or a test suite, which should be ignored.

#### `--no-progress-bar`
Disable progress bar.
#### `--report-slowest-tests INT`
Print slowest tests at the end.
#### `--safe-collecting`
Uses cairo compiler for test collection
#### `--seed INT`
Set a seed to use for all fuzz tests.
### `update`
```shell
$ protostar update cairo-contracts
```
Update a dependency or dependencies. If the default branch of a dependency's repository uses tags, Protostar will pull a commit marked with the newest tag. Otherwise, Protostar will pull a recent commit from the default branch.
#### `package STRING`
- `GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]`
    - `OpenZeppelin/cairo-contracts@0.1.0`
- `URL_TO_THE_REPOSITORY`
    - `https://github.com/OpenZeppelin/cairo-contracts`
- `SSH_URI`
    - `git@github.com:OpenZeppelin/cairo-contracts.git`
- `PACKAGE_DIRECTORY_NAME`
    - `cairo_contracts`, if the package location is `lib/cairo_contracts`
### `upgrade`
```shell
$ protostar upgrade
```
Upgrade Protostar.