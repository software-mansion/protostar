# Invoking contracts

## Overview
This command allows you to send an invoke transaction with `@external` function entrypoint.

The basic inputs that you need for the commands are:

- [Signing credentials](#signing)
- Contract address
- Function name
- Inputs to the function
- Fee specification (concrete amount, or auto-estimation)
- Network you want to target (i.e. its name or gateway URL)

For detailed API description, see [invoke command reference](../../cli-reference.md#invoke).

## Signing
Credentials for paying the fee are needed, which are:

- Account address (which pays the fee) - in hex (prefixed with '0x') or decimal representation.
- Private key for that account (from ArgentX, Braavos etc.) - in hex (prefixed with '0x') or decimal representation. This can be provided with `PROTOSTAR_ACCOUNT_PRIVATE_KEY` env variable or with a file on local filesystem containing that key in plaintext, in which case you should use `--private-key-path`.

Custom signing logic is made possible by using custom signers - see details [here](./06-signing.md).

## Usage example

```shell 
protostar invoke --contract-address 0x4a739ab73aa3cac01f9da5d55f49fb67baee4919224454a2e3f85b16462a911 --function "setter_tester_success" --network testnet --account-address 0x0481Eed2e02b1ff19Fd32429801f28a59DEa630d81189E39c80F2F60139b381a --max-fee auto --inputs 3 --private-key-path ./.pkey
Invoke transaction was sent.
Transaction hash: 0x05d2362b9b5a5aba8a02a41d2f1fcbdc06cde89f90cf33c0ea4957846c86aeef
```
:::warning
Setting `max-fee` to `auto` is discouraged, since it may incur extra unexpected costs.
:::

:::note
Inputs have to be passed either as a list of felts (integers) (`1 2 3`), like Cairo calldata, or as a dict with arguments' names mapped to their values (`a=11 b=12 c=13`).
If your function requires structures, arrays, or tuples, you should manually serialize it, as
shown in [Cairo documentation](https://www.cairo-lang.org/docs/hello_starknet/more_features.html#array-arguments-in-calldata).
:::

:::note
If you need to print machine-readable output in JSON format, you should use `--json` flag.

This may come in handy for writing scripts that include protostar commands.

For more information, go to [this page](./scripting.md)
:::
