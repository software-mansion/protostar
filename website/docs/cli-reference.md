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
### `cairo-migrate`
Migrates the project sources to be compatible with cairo 0.10
#### `targets STRING[]=[PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/cairo/protostar/_utils.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/cairo/protostar/asserts.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/templates/default/tests/test_main.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/templates/default/src/main.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/lang/compiler/lib/registers.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/bool.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/default_dict.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/merkle_update.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/squash_dict.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/set.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/memset.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/find_element.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/registers.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/patricia.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/math_cmp.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/hash_chain.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/hash_state.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/pow.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/memcpy.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/dict.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/segments.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/merkle_multi_update.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/signature.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/cairo_builtins.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/ec.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/hash.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/serialize.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/small_merkle_tree.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/ec_point.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/math.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/alloc.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/uint256.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/dict_access.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/bitwise.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/keccak.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/usort.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/invoke.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/cairo_blake2s/packed_blake2s.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/cairo_blake2s/blake2s.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/cairo_secp/bigint.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/cairo_secp/field.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/cairo_secp/signature.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/cairo_secp/ec.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/cairo_secp/constants.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/cairo_keccak/packed_keccak.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/cairo/common/cairo_keccak/keccak.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/starknet/core/os/contracts.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/starknet/core/os/contract_address/contract_address.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/starknet/common/eth_utils.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/starknet/common/storage.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/starknet/common/messages.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/dist/protostar/starkware/starknet/common/syscalls.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/testing_hooks/testing_hooks_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/testing_hooks/setup_case_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/testing_hooks/invalid_setup_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/testing_hooks/basic_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/fuzzing/non_felt_parameter_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/fuzzing/state_isolation_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/fuzzing/max_examples_in_setup_hook_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/fuzzing/hypothesis_multiple_errors_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/fuzzing/max_examples_invalid_arguments_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/fuzzing/max_examples_in_setup_case_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/fuzzing/basic_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/project_compiler/project_compiler_test/compilation_error/invalid_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/project_compiler/project_compiler_test/importing/utils.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/project_compiler/project_compiler_test/importing/entry_point.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/project_compiler/project_compiler_test/importing/modules/some_lib/constants.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/constructor_in_tested_file/basic_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/constructor_in_tested_file/basic_contract_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/fuzzing_strategies/edge_cases_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/fuzzing_strategies/integers_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/fuzzing_strategies/integers_unbounded_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/testing_output/testing_output_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/testing_output/hash.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/asserts/asserts_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/testing_timing/testing_timing_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/compilation/collector_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/compilation/contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/compilation/namespace_constructor.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/compilation/test_unit_with_constructor.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/compilation/basic_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/compilation/test_unit_with_namespace_constructor.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/data/library/external_library.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/expect_events/expect_events_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/expect_events/basic_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/roll/roll_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/roll/block_number_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/declare_contract/contract_with_invalid_hint.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/declare_contract/disabling_hint_validation_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/prepare/basic_with_constructor_uint256.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/prepare/prepare_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/reflect/reflect_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/mock_call/balance_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/mock_call/mocked.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/mock_call/mock_call_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/mock_call/delegate_proxy.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/mock_call/proxy.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/declare/declare_contract_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/declare/proxy_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/declare/basic_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/prank/pranked.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/prank/prank_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/load/load_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/load/block_number_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/warp/warp_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/warp/timestamp_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/expect_revert/expect_revert_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/assume_and_reject/assume_and_reject_together_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/assume_and_reject/assume_and_reject_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/deploy_contract/basic_with_constructor_uint256.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/deploy_contract/contract_using_external.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/deploy_contract/deploy_contract_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/deploy_contract/basic_with_constructor.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/deploy_contract/pranked_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/deploy_contract/proxy_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/deploy_contract/basic_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/store/block_number_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/integration/cheatcodes/store/store_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/benchmarks/basic.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/test_deploying/contract_with_constructor.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/test_migrating/migration_signed_invokes.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/test_migrating/migration_up_down.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/test_migrating/box_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/test_broken.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/contract_with_invalid_hint.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/test_assume_and_reject.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/test_print_failed.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/main_using_simple_function.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/test_print_only_setup.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/main_with_execute.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/test_fuzz.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/basic.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/test_failed.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/test_proxy.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/unformatted.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/test_print_passed.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/test_main_using_simple_function.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/proxy_contract.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/formatted.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/simple_function.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/test_main_with_execute.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/tests/e2e/fixtures/contract_with_invalid_hint_test.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/protostar/commands/test/examples/basic.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/protostar/commands/test/examples/basic_with_constructor.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/protostar/commands/test/examples/fuzzing/test_fuzz.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/protostar/commands/test/examples/broken/test_basic_broken.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/protostar/commands/test/examples/broken/basic_broken.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/protostar/commands/test/examples/empty/test_no_test_functions.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/protostar/commands/test/examples/basic/test_basic.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/protostar/commands/test/examples/invalid/test_invalid_syntax.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/protostar/commands/test/examples/failure/test_basic_failure.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/cairo/protostar/_utils.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/cairo/protostar/asserts.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/templates/default/tests/test_main.cairo'), PosixPath('/Users/timelock/swm/starkware/protostar/templates/default/src/main.cairo')]`
Targets to migrate (a target can be a file or directory)
### `declare`
Sends a declare transaction to StarkNet.
#### `contract PATH`
Required.

Path to compiled contract.
#### `--account-address STRING`
Account address
#### `--chain-id INT`
The chain id. It is required unless `--network` is provided.
#### `--gateway-url STRING`
The URL of a StarkNet gateway. It is required unless `--network` is provided.
#### `-n` `--network STRING`
The name of the StarkNet network.
It is required unless `--gateway-url` is provided.

Supported StarkNet networks:
- `testnet`
- `mainnet`
- `alpha-goerli`
- `alpha-mainnet`
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
protostar deploy ./build/main.json --network alpha-goerli
```
Deploy contracts.
#### `contract PATH`
Required.

The path to the compiled contract.
#### `--chain-id INT`
The chain id. It is required unless `--network` is provided.
#### `--gateway-url STRING`
The URL of a StarkNet gateway. It is required unless `--network` is provided.
#### `-i` `--inputs FELT[]`
The inputs to the constructor. Calldata arguments may be of any type that does not contain pointers.
[Read more about representing Cairo data types in the CLI.](https://www.cairo-lang.org/docs/hello_starknet/more_features.html#array-arguments-in-calldata)
#### `-n` `--network STRING`
The name of the StarkNet network.
It is required unless `--gateway-url` is provided.

Supported StarkNet networks:
- `testnet`
- `mainnet`
- `alpha-goerli`
- `alpha-mainnet`
#### `--salt FELT`
An optional salt controlling where the contract will be deployed. The contract deployment address is determined by the hash of contract, salt and caller. If the salt is not supplied, the contract will be deployed with a random salt.
#### `--token STRING`
Used by whitelisted users for deploying contracts in Alpha MainNet.
#### `--wait-for-acceptance`
Waits for transaction to be accepted on chain.
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
#### `--account-address STRING`
Account address
#### `--chain-id INT`
The chain id. It is required unless `--network` is provided.
#### `--gateway-url STRING`
The URL of a StarkNet gateway. It is required unless `--network` is provided.
#### `-n` `--network STRING`
The name of the StarkNet network.
It is required unless `--gateway-url` is provided.

Supported StarkNet networks:
- `testnet`
- `mainnet`
- `alpha-goerli`
- `alpha-mainnet`
#### `--no-confirm`
Skip confirming building the project.
#### `--output-dir PATH`
Migration output directory.
#### `--private-key-path PATH`
Path to the file, which stores your private key (in hex representation) for the account. 
Can be used instead of PROTOSTAR_ACCOUNT_PRIVATE_KEY env variable.
#### `--rollback`
Run `rollback` function in the migration script.
#### `--signer-class STRING`
Custom signer class module path.
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
#### `--no-progress-bar`
Disable progress bar.
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