# `invoke`

```python
def invoke(
    contract_address: int,
    function_name: str,
    inputs: list[int] | dict[str, Any] | None = None,
    config: SignedCheatcodeConfig,
    *,
) -> None:
```

This cheatcode invokes a StarkNet contract, with possible state changes. Can be useful for initializing proxies, etc.
`SignedCheatcodeConfig` stores configuration used in cheatcodes that can be signed.

It's an extension of [CheatcodeNetworkConfig](../03-network-config.md), so it's properties are applicable here as well.

```python
from protostar.starknet_gateway import Fee
class SignedCheatcodeConfig(CheatcodeNetworkConfig):
    max_fee: Fee
```

Auto-fee estimation is supported, and `starknet.py`'s estimation logic is used - see [starknet.py docs](https://starknetpy.readthedocs.io/en/latest/guide.html#automatic-fee-estimation).


:::tip
You can provide `inputs` as a dictionary to use [data transformer](./README.md#data-transformer).
:::

## Fees
We recommend using `max_fee` to avoid unexpected network costs.

The config object is passed as a python dictionary.

This config object also contains properties of `CheatcodeNetworkConfig`, see configuration options in the [related docs](../03-network-config.md).

Wallet used for providing the fee is global, and is provided with signing arguments, as described [here](../01-cli.md#signing-a-declaration).

## Example

```
$ protostar migrate migrations/migration_01.cairo
    --network alpha-goerli
    --output-dir migrations/output
    --private-key-path ./pkey
    --account-address 0x1231231212321
```

```cairo title="migrations/migration_01.cairo"
%lang starknet

@external
func up() {
    %{
        contract_address = deploy_contract(
             "./build/main.json",
             config={"wait_for_acceptance": True}
        ).contract_address

        invoke(
            contract_address,
            "initialize",
            {"new_authority": 123},
            config={
                "wait_for_acceptance": True,
                "max_fee": "auto",
            }
        )
    %}

    return ();
}
```

```cairo title="src/main.cairo"
%lang starknet

@storage_var
func authority() -> (res: felt) {
}

@external
func initialize{
    syscall_ptr: felt*,
    pedersen_ptr: HashBuiltin*,
    range_check_ptr
}(new_authority: felt) {
    let (authority_now) = authority.read();
    tempvar syscall_ptr = syscall_ptr;
    tempvar pedersen_ptr = pedersen_ptr;
    tempvar range_check_ptr = range_check_ptr;

    if (authority_now != 0) {
        with_attr error_message("Authority has already been set") {
            assert 1 = 0;
        }
        tempvar syscall_ptr = syscall_ptr;
        tempvar pedersen_ptr = pedersen_ptr;
        tempvar range_check_ptr = range_check_ptr;
    }

    authority.write(new_authority);
    return ();
}
```
