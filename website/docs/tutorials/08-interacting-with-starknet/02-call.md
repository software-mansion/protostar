# Calling contracts

## Overview

This cheatcode allows you to call any `@view` function without mutating the blockchain state.  

For detailed API description, see [call command reference](../../cli-reference.md#call).

The basic inputs that you need for the commands are:
- Contract address
- Function name
- Inputs to the function
- Network you want to target (i.e. its name or gateway URL)

## Usage example

```shell 
protostar call --contract-address 0x07ee8ac4d0c1b11eca79b347fb47be5a431cf84a854542b9fbe14f11cfba5466 --function "add_3" --network testnet --inputs 3
15:07:34 [INFO] Call successful.
Response:
{
    "res": 6
}
15:07:35 [INFO] Execution time: 2.20 s
```

:::note
Inputs have to be passed as list of felts (integers), like cairo calldata. If your function requires structures, arrays, or tuples, you should manually serialize it, as shown [in the cairo-lang docs](https://www.cairo-lang.org/docs/hello_starknet/more_features.html#array-arguments-in-calldata).
:::