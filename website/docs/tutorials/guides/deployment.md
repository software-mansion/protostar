---
sidebar_label: Deployment
---

# Deployment

Protostar `>=0.2.1` supports deploying smart contracts to a given network with the `protostar deploy` command. It has similar interface to `starknet deploy` command. [Read the CLI reference for the deploy command](/docs/cli-reference#deploy) to learn more about all supported arguments.

## Example — deploying the default contract
1. Create new project 
   ```bash
   $ protostar init
   ```
2. Build the project
   ```bash
   $ protostar build
   ```
3. Deploy the contract to the testnet
   ```
   $ protostar deploy ./build/main.json --network alpha-goerli
   ```
    ```shell title="Deployment output"
    [INFO] Deploy transaction was sent.
    Contract address: 0x06a5ea9e42c921bd58e24b8da9d1fc91a488df0700b173f1c6bb0e453f68afec
    Transaction hash: 0x1cbba90ba0d1fbfba09b1f7a0f987134dd9a02a845ca89244b3272374d37ede

    https://goerli.voyager.online/contract/0x06a5ea9e42c921bd58e24b8da9d1fc91a488df0700b173f1c6bb0e453f68afec
    ```

## Using [configuration profiles](/docs/tutorials/project-initialization#configuration-profiles)
Configuration profiles allow you to easily reuse configuration for devnet, testnet, and mainnet networks. You can do it by defining the following configuration profiles in the `protostar.toml` as demonstrated on the snippet below.

```toml title=protostar.toml
# ...

# https://github.com/Shard-Labs/starknet-devnet
[profile.devnet.protostar.deploy]
gateway_url="http://127.0.0.1:5050/"

[profile.testnet.protostar.deploy]
network="alpha-goerli"

[profile.mainnet.protostar.deploy]
network="alpha-mainnet"
```

Then, run `deploy` command with the `--profile` argument.
```bash
protostar -p devnet deploy ./build/main.json
```
