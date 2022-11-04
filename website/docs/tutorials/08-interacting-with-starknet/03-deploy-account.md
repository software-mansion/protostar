# Creating account

## Overview

In order to create a new account, you need to deploy an account contract. StarkNet expects a certain interface from an account contract. [OpenZeppelin](https://github.com/OpenZeppelin/cairo-contracts/blob/main/src/openzeppelin/account/presets/Account.cairo) and [ArgentX](https://github.com/argentlabs/argent-contracts-starknet/blob/develop/contracts/account/ArgentAccount.cairo) provide account contract implementations that you can use.

There are two ways of deploying a new account contract:
- sending `DEPLOY_ACCOUNT` transaction
- using already deployed account contract and [UDC](https://community.starknet.io/t/universal-deployer-contract-proposal/1864)

## Sending `DEPLOY_ACCOUNT` transaction 

Protostar allows you to send the `DEPLOY_ACCOUNT` transaction from the CLI by calling the [`deploy-account` command](/docs/cli-reference#deploy-account).
However, before you send such transaction you need to:
1. find class hash of the account contract you want to be deployed and supports `DEPLOY_ACCOUNT` transaction
2. [calculate the account contract address](https://github.com/starkware-libs/cairo-lang/blob/ed6cf8d6cec50a6ad95fa36d1eb4a7f48538019e/src/starkware/starknet/services/api/gateway/contract_address.py#L12)
3. [prefund the account contract](https://docs.starknet.io/documentation/Ecosystem/ref_operational_info/#bridged_tokens)
