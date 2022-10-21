## Details
This cheatcode allows you to call any `@view` function without mutating the blockchain state.  
## Usage
```
protostar call [-h] [--gateway-url GATEWAY_URL] [--chain-id CHAIN_ID] [--network NETWORK] [--contract-address CONTRACT_ADDRESS] [--function FUNCTION] [--inputs [INPUTS ...]]

optional arguments:
  -h, --help            show this help message and exit
  --gateway-url GATEWAY_URL
                        The URL of a StarkNet gateway. It is required unless `--network` is provided.
  --chain-id CHAIN_ID   The chain id. It is required unless `--network` is provided.
  --network NETWORK, -n NETWORK
                        The name of the StarkNet network.
                        It is required unless `--gateway-url` is provided.

                        Supported StarkNet networks:
                        - `testnet`
                        - `mainnet`
                        - `alpha-goerli`
                        - `alpha-mainnet`
  --contract-address CONTRACT_ADDRESS
                        The address of the contract being called.
  --function FUNCTION   The name of the function being called.
  --inputs [INPUTS ...]
                        Inputs to the function being called, represented by a list of space-delimited values.
```
:::note
Inputs have to be passed as list of felts (integers), like cairo calldata. If your function requires structures, arrays, or tuples, you should manually serialize it, as shown [in the cairo-lang docs](https://www.cairo-lang.org/docs/hello_starknet/more_features.html#array-arguments-in-calldata).
:::

## Example

```shell 
protostar call --contract-address 0x07ee8ac4d0c1b11eca79b347fb47be5a431cf84a854542b9fbe14f11cfba5466 --function "add_3" --network testnet --inputs 3
15:07:34 [INFO] Call successful.
Response:
{
    "res": 6
}
15:07:35 [INFO] Execution time: 2.20 s
```