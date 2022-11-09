# Deploying new contracts

## Overview
Protostar supports deploying smart contracts to a given network with the `protostar deploy` command. 
It has a similar interface to the `starknet deploy` command. 

The basic inputs needed for this command are:
- Path to the compiled contract file
- Network you want to target (i.e. its name or gateway URL)
[Read the CLI reference for the deploy command](../../cli-reference.md#deploy) to learn more about all supported arguments.

:::caution
The deploy transaction will be deprecated in future StarkNet versions. 
To deploy new contract instances, you can use the deploy syscall. 
For more information, read [StarkNet's Contract Classes documentation](https://docs.starknet.io/docs/Contracts/contract-classes).
:::

:::info
This command will be reworked to be compatible with the [UDC concept](https://community.starknet.io/t/universal-deployer-contract-proposal/1864). 
:::

## Usage example
After [compiling your contract](../compiling), you can deploy the contract in the following way.

```console title="protostar deploy ./build/main.json --network testnet"
[INFO] Deploy transaction was sent.
Contract address: 0x06a5ea9e42c921bd58e24b8da9d1fc91a488df0700b173f1c6bb0e453f68afec
Transaction hash: 0x1cbba90ba0d1fbfba09b1f7a0f987134dd9a02a845ca89244b3272374d37ede

https://goerli.voyager.online/contract/0x06a5ea9e42c921bd58e24b8da9d1fc91a488df0700b173f1c6bb0e453f68afec
```
