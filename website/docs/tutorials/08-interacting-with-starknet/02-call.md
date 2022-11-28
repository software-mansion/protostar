# Calling contracts

## Overview

The `protostar call` command allows you to call any `@view` function without mutating the blockchain
state.  

The basic inputs that you need for the commands are:

- Contract address
- Function name
- Inputs to the function
- Network you want to target (i.e. its name or gateway URL)

For detailed API description, see [call command reference](../../cli-reference.md#call).

## Usage example

```shell 
protostar call --contract-address 0x07ee8ac4d0c1b11eca79b347fb47be5a431cf84a854542b9fbe14f11cfba5466 --function "add_3" --network testnet --inputs 3
Call successful.
Response:
{
    "res": 6
}
```

:::note
Inputs have to be passed either as a list of felts (integers) (`1 2 3`), like Cairo calldata, or as a dict with arguments' names mapped to their values (`a=11 b=12 c=13`).
If your function requires structures, arrays, or tuples, you should manually serialize it, as
shown in [Cairo documentation](https://www.cairo-lang.org/docs/hello_starknet/more_features.html#array-arguments-in-calldata).
:::
