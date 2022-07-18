---
sidebar_label: Deploying
---

# Deploying

## Prerequisites
- [Factory Contract pattern](https://research.csiro.au/blockchainpatterns/general-patterns/contract-structural-patterns/factory-contract/)
- [Deploying a contract by another contract](https://www.cairo-lang.org/docs/hello_starknet/deploying_from_contracts.html?highlight=class%20hash)

## Declaring a contract
StarkNet separates contracts into classes and instances. To create a new contract, you need to:
1. declare a class
2. call the deploy syscall with the `class_hash` from the declare transaction as an argument
   ```cairo
   from starkware.starknet.common.syscalls import deploy
   ```
   
To declare a contract from the Protostar CLI you need to build your project and use the `protostar declare` command.

```text
$ protostar declare ./build/main.json --network alpha-goerli
```

```text title="The result of running 'protostar declare'."
[INFO] Declare transaction was sent.
Class hash: 0x038cc...
Transaction hash: 0x3c6c...

https://goerli.voyager.online/contract/0x038cc...
```

## Deploying
:::caution
The deploy transaction will be deprecated in future StarkNet versions. To deploy new contract instances, you can use the deploy syscall. For more information, read [StarkNet's Contract Classes documentation](https://docs.starknet.io/docs/Contracts/contract-classes).
:::

Protostar supports deploying smart contracts to a given network with the `protostar deploy` command. It has a similar interface to the `starknet deploy` command. [Read the CLI reference for the deploy command](/docs/cli-reference#deploy) to learn more about all supported arguments.

### Example — deploying the default contract
After [compiling your contract](/docs/tutorials/guides/compiling), you can deploy the contract in the following way.

```
$ protostar deploy ./build/main.json --network alpha-goerli
```
  
 ```text title="Deployment output"
[INFO] Deploy transaction was sent.
Contract address: 0x06a5ea9e42c921bd58e24b8da9d1fc91a488df0700b173f1c6bb0e453f68afec
Transaction hash: 0x1cbba90ba0d1fbfba09b1f7a0f987134dd9a02a845ca89244b3272374d37ede

https://goerli.voyager.online/contract/0x06a5ea9e42c921bd58e24b8da9d1fc91a488df0700b173f1c6bb0e453f68afec
```

## Using [configuration profiles](/docs/tutorials/project-initialization#configuration-profiles)
Configuration profiles allow you to easily reuse configuration for devnet, testnet, and mainnet networks. You can define a network configuration in the `protostar.toml` as demonstrated in the snippet below.

```toml title=protostar.toml
# ...

# https://github.com/Shard-Labs/starknet-devnet
[profile.devnet.protostar.deploy]
gateway-url="http://127.0.0.1:5050/"

[profile.testnet.protostar.deploy]
network="alpha-goerli"

[profile.mainnet.protostar.deploy]
network="alpha-mainnet"
```

Then, run `deploy` command with the `--profile` argument.
```text
protostar -p devnet deploy ./build/main.json
```
