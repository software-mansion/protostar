---
sidebar_label: CLI
---

# Deployment CLI
Protostar offers similar CLI to [StarkNet's CLI](https://docs.starknet.io/docs/CLI/commands). However, with Protostar you can move deployment configuration to [`protostar.toml`](/docs/tutorials/project-initialization#protostartoml) and display help for each command.



## Declaring a contract

StarkNet provides a distinction between contract class and instance. To create a new contract, you need to:
1. Declare a contract
2. Use the deploy syscall with the `class_hash` from the declare transaction as an argument
   ```cairo
   from starkware.starknet.common.syscalls import deploy
   ```
   
To declare a contract from the Protostar CLI you need to build your project and use the `protostar declare` command.

```console title="protostar declare ./build/main.json --network alpha-goerli"
[INFO] Declare transaction was sent.
Class hash: 0x038cc...
Transaction hash: 0x3c6c...

https://goerli.voyager.online/contract/0x038cc...
```

### Signing a declaration

Since Cairo v0.10 declare transactions can be signed.
Protostar offers two ways of providing the signature:

### 1. StarkCurveSigner

By default, Protostar uses the [StarkCurveSigner class](https://starknetpy.readthedocs.io/en/latest/signer.html#starknet_py.net.signer.stark_curve_signer.StarkCurveSigner) from Starknet.py.

This way requires you to pass a private key (for signing) and account contract's address (to fetch the nonce).
You can obtain the key and account address i.e. from [Argentx](https://chrome.google.com/webstore/detail/argent-x/dlcobpjiigpikoobohmabehhmhfoodbb) or [Braavos](https://chrome.google.com/webstore/detail/braavos-wallet/jnlgamecbpmbajjfhmmmlhejkemejdma) wallets. 

2 options are used for this:
- `private-key-path` - a path to the file containing hex-encoded private key
- `account-address` - your account contract's address (hex-encoded as well) on the appropriate network

Alternatively, if you prefer not to store private key in a file, we check for `ACCOUNT_PRIVATE_KEY` environment variable, and use it if it's available.   
It should be in the same hex-encoded format, like all the options above.

### 2. Using a custom signer class

You can provide a custom signer class which inherits from [BaseSigner](https://starknetpy.readthedocs.io/en/latest/signer.html#starknet_py.net.signer.BaseSigner) abstract class. 
This way of signing requires you to write a class in Python, which signs the transaction in a way that is suitable to you.
After writing such class, simply use `signer_class` argument in the CLI for `declare` command to use that class instead of the default one.
Usage of this way of signing is exclusive with the default signer strategy.

:::caution
The custom signer class must not take any arguments in the constructor, since we don't pass any args on instantiation.
:::

The Python file containing this class can be put next to Cairo source code.
Protostar synchronizes `PYTHONPATH` with project's `cairo_path`.
Modules that are dependencies of Protostar (like `starknet_py` or `cairo-lang`) should be available for importing by default.
If you want to import other custom modules, you should extend `PYTHONPATH` yourself (https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH), when running this command.

## Deploying
:::caution
The deploy transaction will be deprecated in future StarkNet versions. To deploy new contract instances, you can use the deploy syscall. For more information, read [StarkNet's Contract Classes documentation](https://docs.starknet.io/docs/Contracts/contract-classes).
:::

Protostar supports deploying smart contracts to a given network with the `protostar deploy` command. It has a similar interface to the `starknet deploy` command. [Read the CLI reference for the deploy command](../../cli-reference.md#deploy) to learn more about all supported arguments.

### Example — deploying the default contract
After [compiling your contract](../04-compiling.md), you can deploy the contract in the following way.

```console title="protostar deploy ./build/main.json --network alpha-goerli"
[INFO] Deploy transaction was sent.
Contract address: 0x06a5ea9e42c921bd58e24b8da9d1fc91a488df0700b173f1c6bb0e453f68afec
Transaction hash: 0x1cbba90ba0d1fbfba09b1f7a0f987134dd9a02a845ca89244b3272374d37ede

https://goerli.voyager.online/contract/0x06a5ea9e42c921bd58e24b8da9d1fc91a488df0700b173f1c6bb0e453f68afec
```

## Using [configuration profiles](../03-project-initialization.md#configuration-profiles)
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
