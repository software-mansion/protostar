# Creating account

## Overview

In order to create a new account, you need to deploy an account contract. StarkNet expects a certain interface from an account contract. [OpenZeppelin](https://github.com/OpenZeppelin/cairo-contracts/blob/main/src/openzeppelin/account/presets/Account.cairo) and [ArgentX](https://github.com/argentlabs/argent-contracts-starknet/blob/develop/contracts/account/ArgentAccount.cairo) provide account contract implementations that you can use.

There are three ways of deploying a new account contract:
- sending [`DEPLOY_ACCOUNT` transaction](https://github.com/starkware-libs/cairo-lang/releases/tag/v0.10.1)
- using already deployed account contract and deploying new one via [the Universal Deployer Contract](https://community.starknet.io/t/universal-deployer-contract-proposal/1864)
- (deprecated) sending [`DEPLOY` transaction](https://docs.starknet.io/documentation/develop/Blocks/transactions/#deploy_transaction)

## Sending `DEPLOY_ACCOUNT` transaction 

Protostar allows you to send the `DEPLOY_ACCOUNT` transaction from the CLI by calling the [`deploy-account` command](/docs/cli-reference#deploy-account).
However, before you send such transaction you need to:
1. Find the class hash of the account contract compatible with `DEPLOY_ACCOUNT` transaction. The entity that declared the account contract should make the class hash easily available. It's recommended to check the README.md in the repository with the source of the account contract:
   - [OpenZeppelin/cairo-contracts](https://github.com/OpenZeppelin/cairo-contracts)
   - [argentlabs/argent-contracts-starknet](https://github.com/argentlabs/argent-contracts-starknet)
2. Calculate the account contract address with [`protostar calculate-account-address` command](/docs/cli-reference#calculate-account-address)
3. Prefund the account contract.
   
    | Network | Recommended method                                                                               |
    | ------- | ------------------------------------------------------------------------------------------------ |
    | devnet  | [Local Faucet](https://shard-labs.github.io/starknet-devnet/docs/guide/mint-token)               |
    | testnet | [StarkNet Faucet](https://faucet.goerli.starknet.io/)                                            |
    | mainnet | [Token Bridge](https://docs.starknet.io/documentation/develop/L1-L2_Communication/token-bridge/) |

