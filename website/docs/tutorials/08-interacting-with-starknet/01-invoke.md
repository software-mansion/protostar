## Details
This cheatcode allows you to send an invoke transaction with `@external` function entrypoint.

### Signing
Credentials for paying the fee are needed, which are: 
- Account address (which pays the fee)
- Private key for that account (from ArgentX, Braavos etc.) - in hex string (i.e. 0xa1c359ef) form. This can be provided with `PROTOSTAR_ACCOUNT_PRIVATE_KEY` env variable or with a file on local filesystem containing that key in plaintext, in which case you should use `--private-key-path`.

Custom signing logic is made possible by using custom signers - see details [here](https://docs.swmansion.com/protostar/docs/tutorials/deploying/cli#2-using-a-custom-signer-class).



:::warning
Setting `max-fee` to `auto` is discouraged, since it may incur extra unexpected costs.
:::

## Usage
```
protostar invoke [-h] [--account-address ACCOUNT_ADDRESS] [--private-key-path PRIVATE_KEY_PATH] [--signer-class SIGNER_CLASS] [--gateway-url GATEWAY_URL] [--chain-id CHAIN_ID] [--network NETWORK] [--contract-address CONTRACT_ADDRESS] [--function FUNCTION] [--inputs [INPUTS ...]]
                                   [--max-fee MAX_FEE] [--wait-for-acceptance]

Arguments:
  -h, --help            show this help message and exit
  --account-address ACCOUNT_ADDRESS
                        Account address
  --private-key-path PRIVATE_KEY_PATH
                        Path to the file, which stores your private key (in hex representation) for the account.
                        Can be used instead of PROTOSTAR_ACCOUNT_PRIVATE_KEY env variable.
  --signer-class SIGNER_CLASS
                        Custom signer class module path.
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
  --max-fee MAX_FEE     The maximum fee that the sender is willing to pay for the transaction. Provide "auto" to auto estimate the fee.
  --wait-for-acceptance
                        Waits for transaction to be accepted on chain.
```
:::note
Inputs have to be passed as list of felts (integers), like cairo calldata. If your function requires structures, arrays, or tuples, you should manually serialize it, as shown [in the cairo-lang docs](https://www.cairo-lang.org/docs/hello_starknet/more_features.html#array-arguments-in-calldata).
:::

## Example

```shell 
PROTOSTAR_ACCOUNT_PRIVATE_KEY=0x<redacted> protostar invoke --contract-address 2104712876024647862991828835908656456713967333335715277181131715044727499025 --function "setter_tester_success" --network testnet --account-address 0x0481Eed2e02b1ff19Fd32429801f28a59DEa630d81189E39c80F2F60139b381a --max-fee auto --inputs 3
16:54:56 [INFO] Invoke transaction was sent.
Transaction hash: 0x05d2362b9b5a5aba8a02a41d2f1fcbdc06cde89f90cf33c0ea4957846c86aeef
16:54:57 [INFO] Execution time: 13.17 s
```