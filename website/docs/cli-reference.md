# CLI Reference
## Common flags
#### `--no-color`
Disable colors.
#### `-p` `--profile STRING`
Specifies active configuration profile defined in the configuration file.
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
#### `--compiled-contracts-dir PATH=build`
An output directory used to put the compiled contracts in.
#### `--disable-hint-validation`
Disable validation of hints when building the contracts.
### `cairo-migrate`
Migrate project sources to Cairo 0.10.
#### `targets STRING[]=['.']`
Targets to migrate (a target can be a file or directory)
### `calculate-account-address`
In order to create an account, you need to prefund the account. To prefund the account you need to know its address. This command calculates the account address.
#### `--account-address-salt INT`
Required.

An arbitrary value used to determine the address of the new contract.
#### `--account-class-hash CLASS_HASH`
Required.

Class hash of the declared account contract.
#### `--account-constructor-input INT[]`
Input to the account's constructor.
#### `--json`
Print machine readable output in JSON format.
### `call`
Calls a contract on StarkNet with given parameters
#### `--chain-id INT`
The chain id. It is required unless `--network` is provided.
#### `--contract-address ADDRESS`
Required.

The address of the contract being called.
#### `--function STRING`
Required.

The name of the function being called.
#### `--gateway-url STRING`
The URL of a StarkNet gateway. It is required unless `--network` is provided.
#### `--inputs FELT[]`
Inputs to the function being called, represented by a list of space-delimited values.
#### `--json`
Print machine readable output in JSON format.
#### `-n` `--network STRING`
The name of the StarkNet network.
It is required unless `--gateway-url` is provided.

Supported StarkNet networks:
- `testnet`
- `mainnet`
### `declare`
Sends a declare transaction to StarkNet.
#### `contract PATH`
Required.

Path to compiled contract.
#### `--account-address ADDRESS`
Account address.
#### `--block-explorer BLOCK_EXPLORER`
Generated links will point to that block explorer. Available values:
- starkscan
- viewblock
- voyager
#### `--chain-id INT`
The chain id. It is required unless `--network` is provided.
#### `--gateway-url STRING`
The URL of a StarkNet gateway. It is required unless `--network` is provided.
#### `--json`
Print machine readable output in JSON format.
#### `--max-fee FEE`
The maximum fee that the sender is willing to pay for the transaction. Provide "auto" to auto estimate the fee.
#### `-n` `--network STRING`
The name of the StarkNet network.
It is required unless `--gateway-url` is provided.

Supported StarkNet networks:
- `testnet`
- `mainnet`
#### `--private-key-path PATH`
Path to the file, which stores your private key (in hex representation) for the account. 
Can be used instead of PROTOSTAR_ACCOUNT_PRIVATE_KEY env variable.
#### `--signer-class STRING`
Custom signer class module path.
#### `--token STRING`
Used for declaring contracts in Alpha MainNet.
#### `--wait-for-acceptance`
Waits for transaction to be accepted on chain.
### `deploy`
```shell
protostar deploy 0x4221deadbeef123 --network testnet
```
Deploy contracts.
#### `class-hash CLASS_HASH`
The hash of the declared contract class.
#### `--account-address ADDRESS`
Account address.
#### `--block-explorer BLOCK_EXPLORER`
Generated links will point to that block explorer. Available values:
- starkscan
- viewblock
- voyager
#### `--chain-id INT`
The chain id. It is required unless `--network` is provided.
#### `--gateway-url STRING`
The URL of a StarkNet gateway. It is required unless `--network` is provided.
#### `-i` `--inputs FELT[]`
The inputs to the constructor. Calldata arguments may be of any type that does not contain pointers.
[Read more about representing Cairo data types in the CLI.](https://www.cairo-lang.org/docs/hello_starknet/more_features.html#array-arguments-in-calldata)
#### `--json`
Print machine readable output in JSON format.
#### `--max-fee FEE`
The maximum fee that the sender is willing to pay for the transaction. Provide "auto" to auto estimate the fee.
#### `-n` `--network STRING`
The name of the StarkNet network.
It is required unless `--gateway-url` is provided.

Supported StarkNet networks:
- `testnet`
- `mainnet`
#### `--private-key-path PATH`
Path to the file, which stores your private key (in hex representation) for the account. 
Can be used instead of PROTOSTAR_ACCOUNT_PRIVATE_KEY env variable.
#### `--salt FELT`
An optional salt controlling where the contract will be deployed. The contract deployment address is determined by the hash of contract, salt and caller. If the salt is not supplied, the contract will be deployed with a random salt.
#### `--signer-class STRING`
Custom signer class module path.
#### `--token STRING`
Used by whitelisted users for deploying contracts in Alpha MainNet.
#### `--wait-for-acceptance`
Waits for transaction to be accepted on chain.
### `deploy-account`
Sends deploy-account transaction. The account contract must be already declared and prefunded.
#### `--account-address ADDRESS`
Account address.
#### `--account-address-salt INT`
Required.

An arbitrary value used to determine the address of the new contract.
#### `--account-class-hash CLASS_HASH`
Required.

Class hash of the declared account contract.
#### `--account-constructor-input INT[]`
Input to the account's constructor.
#### `--chain-id INT`
The chain id. It is required unless `--network` is provided.
#### `--gateway-url STRING`
The URL of a StarkNet gateway. It is required unless `--network` is provided.
#### `--json`
Print machine readable output in JSON format.
#### `--max-fee WEI`
Required.

Max amount of Wei you are willing to pay for the transaction
#### `-n` `--network STRING`
The name of the StarkNet network.
It is required unless `--gateway-url` is provided.

Supported StarkNet networks:
- `testnet`
- `mainnet`
#### `--nonce INT`
Protects against the replay attacks.
#### `--private-key-path PATH`
Path to the file, which stores your private key (in hex representation) for the account. 
Can be used instead of PROTOSTAR_ACCOUNT_PRIVATE_KEY env variable.
#### `--signer-class STRING`
Custom signer class module path.
### `format`
```shell
$ protostar format
```
Format Cairo source code.
#### `target STRING[]=['.']`
Target to format, can be a file or a directory.
#### `-c` `--check`
Run in 'check' mode. Exits with 0 if input is formatted correctly.Exits with 1 if formatting is required.
#### `--ignore-broken`
Ignore broken files.
#### `--verbose`
Log information about already formatted files as well.
### `init`
```shell
$ protostar init
```
Create a Protostar project.
#### `name STRING`
Name of the directory a new project will be placed in.Ignored when `--existing` is passed.
#### `--existing`
Adapt current directory to a Protostar project.
### `install`
```shell
$ protostar install https://github.com/OpenZeppelin/cairo-contracts
```
Install a dependency as a git submodule.
#### `package STRING`
- `GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]`
    - `OpenZeppelin/cairo-contracts@v0.4.0`
- `URL_TO_THE_REPOSITORY`
    - `https://github.com/OpenZeppelin/cairo-contracts`
- `SSH_URI`
    - `git@github.com:OpenZeppelin/cairo-contracts.git`

#### `--lib-path PATH`
Directory containing project dependencies. This argument is used with the configuration file V2.
#### `--name STRING`
A custom package name. Use it to resolve name conflicts.
### `invoke`
Sends an invoke transaction to the StarkNet sequencer.
#### `--account-address ADDRESS`
Account address.
#### `--block-explorer BLOCK_EXPLORER`
Generated links will point to that block explorer. Available values:
- starkscan
- viewblock
- voyager
#### `--chain-id INT`
The chain id. It is required unless `--network` is provided.
#### `--contract-address ADDRESS`
Required.

The address of the contract being called.
#### `--function STRING`
Required.

The name of the function being called.
#### `--gateway-url STRING`
The URL of a StarkNet gateway. It is required unless `--network` is provided.
#### `--inputs FELT[]`
Inputs to the function being called, represented by a list of space-delimited values.
#### `--json`
Print machine readable output in JSON format.
#### `--max-fee FEE`
The maximum fee that the sender is willing to pay for the transaction. Provide "auto" to auto estimate the fee.
#### `-n` `--network STRING`
The name of the StarkNet network.
It is required unless `--gateway-url` is provided.

Supported StarkNet networks:
- `testnet`
- `mainnet`
#### `--private-key-path PATH`
Path to the file, which stores your private key (in hex representation) for the account. 
Can be used instead of PROTOSTAR_ACCOUNT_PRIVATE_KEY env variable.
#### `--signer-class STRING`
Custom signer class module path.
#### `--wait-for-acceptance`
Waits for transaction to be accepted on chain.
### `migrate`
Run migration file.
#### `path PATH`
Required.

Path to the migration file.
#### `--account-address ADDRESS`
Account address.
#### `--chain-id INT`
The chain id. It is required unless `--network` is provided.
#### `--compiled-contracts-dir PATH=build`
A directory in which your compiled contracts are located (used for deploys and declares)
#### `--gateway-url STRING`
The URL of a StarkNet gateway. It is required unless `--network` is provided.
#### `-n` `--network STRING`
The name of the StarkNet network.
It is required unless `--gateway-url` is provided.

Supported StarkNet networks:
- `testnet`
- `mainnet`
#### `--no-confirm`
Skip confirming building the project.
#### `--private-key-path PATH`
Path to the file, which stores your private key (in hex representation) for the account. 
Can be used instead of PROTOSTAR_ACCOUNT_PRIVATE_KEY env variable.
#### `--signer-class STRING`
Custom signer class module path.
### `migrate-configuration-file`
Migrate protostar.toml V1 to V2.
### `remove`
```shell
$ protostar remove cairo-contracts
```
Remove a dependency.
#### `package STRING`
Required.

- `GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]`
    - `OpenZeppelin/cairo-contracts@v0.4.0`
- `URL_TO_THE_REPOSITORY`
    - `https://github.com/OpenZeppelin/cairo-contracts`
- `SSH_URI`
    - `git@github.com:OpenZeppelin/cairo-contracts.git`
- `PACKAGE_DIRECTORY_NAME`
    - `cairo_contracts`, if the package location is `lib/cairo_contracts`
#### `--lib-path PATH`
Directory containing project dependencies. This argument is used with the configuration file V2.
### `test`
```shell
$ protostar test
```
Execute tests.
#### `target STRING[]=['.']`
A glob or globs to a directory or a test suite, for example:
- `tests/**/*_main*::*_balance` — find test cases, which names ends with `_balance` in test suites with the `_main` in filenames in the `tests` directory,
- `::test_increase_balance` — find `test_increase_balance` test_cases in any test suite within the project.
#### `--cairo-path DIRECTORY[]`
Additional directories to look for sources.
#### `--disable-hint-validation`
Disable hint validation in contracts declared by the `declare` cheatcode or deployed by `deploy_contract` cheatcode.
#### `-x` `--exit-first`
Exit immediately on first broken or failed test.
#### `-i` `--ignore STRING[]`
A glob or globs to a directory or a test suite, which should be ignored.
#### `-lf` `--last-failed`
Only re-run failed and broken test cases.
#### `--max-steps INT`
Set Cairo execution step limit.
#### `--no-progress-bar`
Disable progress bar.
#### `--profiling`
Run profiling for a test contract. Works only for a single test case.Protostar generates a file that can be opened with https://github.com/google/pprof
#### `--report-slowest-tests INT`
Print slowest tests at the end.
#### `--safe-collecting`
Use Cairo compiler for test collection.
#### `--seed INT`
Set a seed to use for all fuzz tests.
### `update`
```shell
$ protostar update cairo-contracts
```
Update a dependency or dependencies. If the default branch of a dependency's repository uses tags, Protostar will pull a commit marked with the newest tag. Otherwise, Protostar will pull a recent commit from the default branch.
#### `package STRING`
- `GITHUB_ACCOUNT_NAME/REPO_NAME[@TAG]`
    - `OpenZeppelin/cairo-contracts@v0.4.0`
- `URL_TO_THE_REPOSITORY`
    - `https://github.com/OpenZeppelin/cairo-contracts`
- `SSH_URI`
    - `git@github.com:OpenZeppelin/cairo-contracts.git`
- `PACKAGE_DIRECTORY_NAME`
    - `cairo_contracts`, if the package location is `lib/cairo_contracts`
#### `--lib-path PATH`
Directory containing project dependencies. This argument is used with the configuration file V2.
### `upgrade`
```shell
$ protostar upgrade
```
Upgrade Protostar.