---
sidebar_label: Migrations
---

# Migrations

:::warning
Breaking changes can be introduced without deprecation. StarkNet [deployment flow can change](https://community.starknet.io/t/universal-deployer-contract-proposal/1864), so Protostar will follow in the future.
:::


Migrations are Cairo files that help you manage contracts on the StarkNet.
These files are responsible for staging your deployment tasks, and they're written under the assumption that your project uses [Proxy Pattern](https://blog.openzeppelin.com/proxy-patterns/).
As your project evolves, you'll create new migration scripts to reflect this evolution on the Starknet.
To interact with StarkNet, you can use [migration cheatcodes](#available-migration-cheatcodes). 

## Creating a migration file
You can create a migration file anywhere, but we recommend creating them inside a `migrations` directory. Currently, Protostar doesn't enforce any naming convention for migration files. In this tutorial we use a naming convention: `migration_NUMBER_TITLE.cairo`, for example `migration_01_init.cairo`.

## Migration file structure
Each migration should have 2 functions: `up` and `down`. The `up` function is responsible to migrate your project forward, and the `down` function is executed to rollback changes. These functions must be decorated with `@external` decorator.

```cairo title="Deploying storage and logic contracts"
%lang starknet

@external
func up() {
    %{
        logic_contract_address = deploy_contract("./build/main.json").contract_address
        storage_contract_address = deploy_contract("./build/proxy.json", [logic_contract_address]).contract_address
    %}
    return ();
}

@external
func down() {
    %{ assert False, "Not implemented" %}
    return ();
}
``` 

## Running the migration
To run the migration execute the `migrate` command. We recommend specifying the migration output directory to save class hashes and contract addresses.

```shell title="Running the migration to the testnet"
protostar migrate migrations/migration_01_init.cairo
    --network testnet
    --output-dir migrations/testnet
```

:::tip
Run `protostar migrate --help` to display all parameters supported by this command.
:::

Protostar asks, if you build the project to prevent you from running the migration on an outdated build output.

```text title="Type 'y' to continue"
Did you build the project before running this command? [y/n]: 
```

:::tip
Run `protostar migrate` with the `--no-confirm` flag to skip this check.
:::


If you build the project, Protostar will print migration logs in the command line.

```text title="You can use this output for the debugging purposes"
[INFO] (Protostar → StarkNet) DECLARE
  contract             /.../protostar/playground/standard/build/main.json
  sender_address       1
  max_fee              0
  version              0
  signature            []
  nonce                0
[INFO] (Protostar ← StarkNet) DECLARE
  code                 TRANSACTION_RECEIVED
  class_hash           123456...
  transaction_hash     0x1234...
[INFO] Migration completed
```

## Lack of Atomicity
If one of the cheatcode fails (e.g. [invoke cheatcode](migrations/invoke)), introduced changes won't be reverted.
```cairo
%lang starknet

@external
func up() { 
    %{ 
        # this deploy won't be reverted
        logic_contract_address = deploy_contract("./build/main.json").contract_address

        # if this deploy fails
        storage_contract_address = deploy_contract("./build/proxy.json", [logic_contract_address]).contract_address 
    %}
    return ();
}

If atomicity is essential and you need only to use deploy and invoke transactions, consider using [Contract Classes](https://docs.starknet.io/documentation/develop/Contracts/contract-classes/).
``` 

## Signing the migration
You can sign the migration's transactions by providing appropriate arguments to the CLI of the command. 
See signing-related documentation [here](../01-cli.md#signing-a-declaration).

For now, declare and invoke migration calls are signed automatically when provided with appropriate arguments.

## Available migration cheatcodes
```mdx-code-block
import DocCardList from '@theme/DocCardList';
import {useCurrentSidebarCategory} from '@docusaurus/theme-common';

<DocCardList items={useCurrentSidebarCategory().items}/>
```
