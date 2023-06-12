# Deploying new contracts

## Overview

Protostar supports deploying smart contracts to a given network with the `protostar deploy` command.

It works by invoking a [Universal Deployer Contract](https://docs.openzeppelin.com/contracts-cairo/0.6.1/udc),
which deploys the contract with the given class hash and constructor arguments.

The basic inputs needed for this command are:

- Class hash of the declared contract class, that you want to deploy
- Network you want to target (i.e. its name or gateway URL)

[Read the CLI reference for the deploy command](../../cli-reference.md#deploy) to learn more about all supported
arguments.

## Usage example

After [declaring your contract](./02-declare.md), you can deploy the contract in the following way.

```shell title="Example"
protostar deploy 0xdeadbeef \
  --network testnet \
  --account-address 0x0481Eed2e02b1ff19Fd32429801f28a59DEa630d81189E39c80F2F60139b381a \
  --max-fee auto \
  --private-key-path ./.pkey
[INFO] Invoke transaction was sent to the Universal Deployer Contract.
Contract address: 0x06a5ea9e42c921bd58e24b8da9d1fc91a488df0700b173f1c6bb0e453f68afec
Transaction hash: 0x1cbba90ba0d1fbfba09b1f7a0f987134dd9a02a845ca89244b3272374d37ede

https://goerli.voyager.online/contract/0x06a5ea9e42c921bd58e24b8da9d1fc91a488df0700b173f1c6bb0e453f68afec
```

:::info
Deploying a contract is a transaction must be signed and requires paying a fee, similarly to how invoke transaction does.
See [signing](./01-invoke.md#signing) for more details.
:::

:::note
If you need to print machine-readable output in JSON format, you should use `--json` flag.

This may come in handy for writing scripts that include Protostar commands.

For more information, go to [this page](./08-scripting.md)
:::