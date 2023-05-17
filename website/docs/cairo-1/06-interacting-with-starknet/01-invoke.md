# Invoking contracts

## Overview

This command allows you to send an invoke transaction to Starknet.

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

- Account address (which pays the fee) - - in hex (prefixed with '0x') or decimal representation.
- Private key for that account (from ArgentX, Braavos etc.) - in hex (prefixed with '0x') or decimal representation.
  This can be provided with `PROTOSTAR_ACCOUNT_PRIVATE_KEY` env variable or with a file on local filesystem containing
  that key in plaintext, in which case you should use `--private-key-path`.

Custom signing logic is made possible by using custom signers - see details [here](./07-signing.md).

## Usage example

```shell title="Example"
protostar invoke \
  --contract-address 0x4a739ab73aa3cac01f9da5d55f49fb67baee4919224454a2e3f85b16462a911 \
  --function "setter_tester_success" \
  --network testnet \
  --account-address 0x0481Eed2e02b1ff19Fd32429801f28a59DEa630d81189E39c80F2F60139b381a \
  --max-fee auto \
  --inputs 3 \
  --private-key-path ./.pkey
Invoke transaction was sent.
Transaction hash: 0x05d2362b9b5a5aba8a02a41d2f1fcbdc06cde89f90cf33c0ea4957846c86aeef
```

To avoid having to repeat `--account-address` and `--private-key-path` in every command, they can be included
in `protostar.toml` configuration profiles. See [this page](./README.md#using-configuration-profiles) for more details.

:::warning
Setting `max-fee` to `auto` is discouraged as it may cause **very high transaction cost**. Always prefer manually
specifying the `max-fee`.
:::

:::note
If you need to print machine-readable output in JSON format, you should use `--json` flag.

This may come in handy for writing scripts that include protostar commands.

For more information, go to [this page](./08-scripting.md)
:::
