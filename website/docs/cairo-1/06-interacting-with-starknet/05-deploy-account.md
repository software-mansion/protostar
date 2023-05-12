# Creating an account

## Overview

In order to create a new account, you need to deploy an account
contract.

There are multiple account contracts to choose from, and it is the end user responsibility to find an account that works
for them. Some examples of already existing account contracts
are [OpenZeppelin](https://github.com/OpenZeppelin/cairo-contracts/blob/main/src/openzeppelin/account/presets/Account.cairo)
and [ArgentX](https://github.com/argentlabs/argent-contracts-starknet/blob/develop/contracts/account/ArgentAccount.cairo).

:::info
You can read more about accounts in
Starknet [here](https://docs.starknet.io/documentation/architecture_and_concepts/Account_Abstraction/introduction/).
:::

There are two ways of deploying a new account contract:

- sending [`DEPLOY_ACCOUNT` transaction](https://github.com/starkware-libs/cairo-lang/releases/tag/v0.10.1)
- using already deployed account contract and deploying new one
  via [the Universal Deployer Contract](https://docs.openzeppelin.com/contracts-cairo/0.6.1/udc)

If you do not have access to any existing account on Starknet, you will most likely have to use the `DEPLOY_ACCOUNT`
transaction.

## Sending `DEPLOY_ACCOUNT` transaction

Protostar allows you to send the `DEPLOY_ACCOUNT` transaction from the CLI by calling
the [`deploy-account` command](/docs/cli-reference#deploy-account).
However, before you send such transaction you need to:

1. Find the class hash of the account contract compatible with `DEPLOY_ACCOUNT` transaction. The entity that declared
   the account contract should make the class hash easily available. The contract must have been
   previously [declared](./02-declare.md) on Starknet by another user.
2. Calculate an account contract address
   with [`protostar calculate-account-address` command](/docs/cli-reference#calculate-account-address)
3. Transfer enough funds to the calculated address to cover the cost of the account deployment.
4. Run the [`deploy-account` command](/docs/cli-reference#deploy-account).

For Starknet testnet you can use [this faucet](https://faucet.goerli.starknet.io/) to obtain testnet ETH.
For mainnet, you will have to bridge enough tokens from other networks.
See [token bridges](https://docs.starknet.io/documentation/architecture_and_concepts/L1-L2_Communication/token-bridge/)
for more details.

