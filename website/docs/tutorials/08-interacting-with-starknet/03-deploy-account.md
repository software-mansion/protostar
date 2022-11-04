# Creating account contract

## Overview

There are two ways of creating a new account contract:
- sending `DEPLOY_ACCOUNT` transaction
- using already deployed account contract

## Sending `DEPLOY_ACCOUNT` transaction 

Protostar allows you to send the `DEPLOY_ACCOUNT` transaction from the CLI by calling the [`deploy-account` command](/docs/cli-reference#deploy-account).
However, before you send such transaction you need to:
1. find class hash of the account contract you want to be deployed and supports `DEPLOY_ACCOUNT` transaction
2. [calculate the account contract address](https://github.com/starkware-libs/cairo-lang/blob/ed6cf8d6cec50a6ad95fa36d1eb4a7f48538019e/src/starkware/starknet/services/api/gateway/contract_address.py#L12)
3. [prefund the account contract](https://docs.starknet.io/documentation/Ecosystem/ref_operational_info/#bridged_tokens)
