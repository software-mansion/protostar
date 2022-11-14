# Declaring new contracts

## Overview
StarkNet provides a distinction between contract class and instance. To deploy a new contract, you need to:
1. Declare a contract
2. Use the deploy syscall with the `class_hash` from the declare transaction as an argument
   ```cairo
   from starkware.starknet.common.syscalls import deploy
   ```

The basic inputs needed for this command are:
- Path to the compiled contract file
- Network you want to target (i.e. its name or gateway URL)

For detailed API description, see [declare command reference](../../cli-reference.md#declare).

## Usage example   
To declare a contract from the Protostar CLI you need to build your project and use the `protostar declare` command.

```console title="protostar declare ./build/main.json --network testnet"
[INFO] Declare transaction was sent.
Class hash: 0x038cc...
Transaction hash: 0x3c6c...

https://goerli.voyager.online/contract/0x038cc...
```
