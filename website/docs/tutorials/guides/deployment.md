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


<!-- - protostar wraps starknet deploy command.  leverage configuration capabilities.

devnet
testnet
mainnet

you need to install starknet if you wish to interact with the contract from the cli -->