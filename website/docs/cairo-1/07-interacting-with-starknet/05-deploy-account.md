# Creating an account

## Overview

In order to create a new account, you need to deploy an account
contract.

:::tip
Instead of manually deploying an account through Protostar, you can consider using
a [wallet provider](https://www.starknet.io/en/ecosystem/wallets). Please note that the Protostar team doesn't verify
the safety or compatibility of these wallets.
:::

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

Protostar supports
sending [`DEPLOY_ACCOUNT`](https://docs.starknet.io/documentation/architecture_and_concepts/Account_Abstraction/deploying_new_accounts/)
transactions.

### Prerequisites

You must know a `class_hash` of already [declared](./02-declare.md) account contract. It will be used to create an
instance of your account.

:::info
Contract used for `DEPLOY_ACCOUNT` transaction define `__validate_deploy__` entrypoint to support creation
through `DEPLOY_ACCOUNT` transaction.
:::

### Precalculating the address

First, calculate the address of the account you will be deploying
using [`protostar calculate-account-address` command](/docs/cli-reference#calculate-account-address).

```shell title="Example"
protostar calculate-account-address \
  --account-address-salt .. \ # provide a valid integer for salt
  --account-class-hash 0x1234 \
  --account-constructor-input 1 2 3 4  
Address: 0x1234   
```

Depending on your account contract used, input expected by the constructor will vary.

### Prefund the calculated address

Transfer enough funds to the calculated address to cover the cost of `DEPLOY_ACCOUNT` transaction.

For Starknet testnet you can use [this faucet](https://faucet.goerli.starknet.io/) to obtain testnet ETH.
For mainnet, you will have to bridge enough tokens from other networks.
See [token bridges](https://docs.starknet.io/documentation/architecture_and_concepts/L1-L2_Communication/token-bridge/)
for more details.

### Deploy the account

Once funds has been transferred to the address, run `protostar deploy-account` command.

```shell title="Example"
protostar deploy-account \
  --account-address-salt .. \ # provide a valid integer for salt
  --account-class-hash 0x1234 \
  --account-constructor-input 1 2 3 4 \
  --network testnet \
  --max-fee 10 \ # provide a valid max-fee in WEI 
  --private-key-path ./.pkey
Transaction hash: 0x060e83c1de4e6ec2cec20239943fd19402f4e23cc88c62afed63f63f6fad4063
```

Once the transaction gets accepted, your account will be available to use at the address you calculated
in [previous step](#precalculating-the-address) using the credentials you provided when sending the transaction.
