---
sidebar_label: Migrations
---

# Migrations

:::warning
Breaking changes can be introduced without depreciation.
:::


Migrations are Cairo files that help you manage contracts on the StarkNet.
They are especially useful, when your project consists of multiple contracts or your project implements [Proxy Pattern](https://blog.openzeppelin.com/proxy-patterns/). Migration code is mainly written in hints.
Protostar injects special functions into hints' scope, which you can use to interact with the StarkNet.
These functions are similar to cheatcodes used to test contracts, hence in this document we will refer to these functions as migration cheatcodes.

## Creating a migration file
You can create a migration file anywhere, but we recommend creating them inside a `migrations` directory. Currently, Protostar doesn't enforce any naming convention for migration files. In this tutorial we use a naming convention: `migration_NUMBER_TITLE.cairo`, for example `migration_01_init.cairo`.

## Migration file structure
Each migration should have 2 functions: `up` and `down`. The `up` function is responsible to migrate your project forward, and the `down` function is executed to rollback changes. These functions must be decorated with `@external` decorator.

```cairo title="Declaring contract in migration file"
%lang starknet

@external
func up() {
    %{ declare("./build/main.json") %}
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
If one of the cheatcode fails (e.g. Invoke Cheatcode), introduced changes won't be reverted. If you need atomicity, move the code to the [Contract Classes](https://docs.starknet.io/documentation/develop/Contracts/contract-classes/).


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
