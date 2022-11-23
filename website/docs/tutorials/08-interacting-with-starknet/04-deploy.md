# Deploying new contracts

## Overview
Protostar supports deploying smart contracts to a given network with the `protostar deploy` command.

It works by invoking a [Universal Deployer Contract](https://community.starknet.io/t/universal-deployer-contract-proposal/1864), 
which deploys the contract with the given class hash and constructor arguments.

The basic inputs needed for this command are:
- Class hash of the declared contract class, that you want to deploy
- Network you want to target (i.e. its name or gateway URL)

[Read the CLI reference for the deploy command](../../cli-reference.md#deploy) to learn more about all supported arguments.

:::caution
Although this command does not require [signing the transaction](./06-signing.md) right now, it is strongly encouraged to do so as it will be required in the future. 
:::

## Usage example
After [declaring your contract](./03-declare.md), you can deploy the contract in the following way.

```console title="protostar deploy 0xdeadbeef --network testnet"
[INFO] Invoke transaction was sent to the Universal Deployer Contract.
Contract address: 0x06a5ea9e42c921bd58e24b8da9d1fc91a488df0700b173f1c6bb0e453f68afec
Transaction hash: 0x1cbba90ba0d1fbfba09b1f7a0f987134dd9a02a845ca89244b3272374d37ede

https://goerli.voyager.online/contract/0x06a5ea9e42c921bd58e24b8da9d1fc91a488df0700b173f1c6bb0e453f68afec
```
