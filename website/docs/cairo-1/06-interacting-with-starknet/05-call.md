# Calling contracts

## Overview

The `protostar call` command allows you to call any `#view` function without mutating the blockchain
state.

The basic inputs that you need for the commands are:

- Contract address
- Function name
- Inputs to the function
- Network you want to target (i.e. its name or gateway URL)

For detailed API description, see [call command reference](../../cli-reference.md#call).

## Usage example

```shell title="Example"
protostar call \
  --contract-address 0x07ee8ac4d0c1b11eca79b347fb47be5a431cf84a854542b9fbe14f11cfba5466 \
  --function "add_3" \
  --network testnet \
  --inputs 3
Call successful.
Response:
{
    "res": 6
}
```

:::note
If you need to print machine-readable output in JSON format, you should use `--json` flag.

This may come in handy for writing scripts that include protostar commands.

For more information, go to [this page](./09-scripting.md)
:::