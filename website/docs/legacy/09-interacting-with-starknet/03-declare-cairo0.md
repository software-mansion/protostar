# Declaring new contracts
:::info
This command can be used to declare Cairo 0 contracts only. 
To declare a Cairo 1 contract, see [`declare` command](../../cairo-1/07-interacting-with-starknet/02-declare.md).
:::
:::warning
This command has been renamed from `declare` and is deprecated. It won't be supported in the future releases. Please consider migrating your contracts to Cairo 1.
:::
## Overview
Starknet provides a distinction between contract class and instance. To deploy a new contract, you need to:
1. Declare a contract
2. Use the deploy syscall with the `class_hash` from the declare transaction as an argument
   ```cairo
   from starkware.starknet.common.syscalls import deploy
   ```

The basic inputs needed for this command are:
- Path to the compiled contract file
- Network you want to target (i.e. its name or gateway URL)

For detailed API description, see [declare-cairo0 command reference](../../cli-reference.md#declare-cairo0).

## Usage example   
To declare a Cairo 0 contract from the Protostar CLI, you need to build your project and use the `protostar declare-cairo0` command.

```console title="protostar declare-cairo0 ./build/main.json --network testnet"
Declare transaction was sent.
Class hash: 0x038cc...
Transaction hash: 0x3c6c...

https://goerli.voyager.online/contract/0x038cc...
```

:::note
If you need to print machine-readable output in JSON format, you should use `--json` flag.

This may come in handy for writing scripts that include protostar commands.

For more information, go to [this page](./scripting.md)
:::