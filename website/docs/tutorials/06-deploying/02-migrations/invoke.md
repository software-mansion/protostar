# `invoke`

```python
def invoke(
    contract_address: int,
    function_name: str,
    inputs: list[int] | dict[str, Any] | None = None,
    max_fee: int | None = None, # in Wei
    auto_estimate_fee: bool = False,
) -> InvokeResult:
```
See full documentation of InvokeResult [here](https://starknetpy.readthedocs.io/en/latest/contract.html#starknet_py.contract.InvokeResult).
Auto-fee estimation is supported, and `starknet.py`'s estimation logic is used - see [starknet.py docs](https://starknetpy.readthedocs.io/en/latest/guide.html?highlight=auto%20estimate#automatic-fee-estimation).

:::warning
Only sync methods are allowed inside of hints! For example, use `wait_for_acceptance_sync` instead of `wait_for_acceptance`.
:::

This cheatcode invokes a StarkNet contract, with possible state changes. Can be useful for initializing proxies, etc.

:::tip
You can provide `inputs` as a dictionary to use [data transformer](./README.md#data-transformer).
:::

## Fees
Either `max_fee` (in Wei) or `auto_estimate_fee` is required.
We recommend using `max_fee` to avoid unexpected costs.

Wallet used for providing the fee is global, and is provided with signing arguments, as described [here](../01-cli.md#signing-a-declaration).

## Example

```
$ protostar migrate migrations/migration_01.cairo
    --network alpha-goerli
    --output-dir migrations/output
    --private-key-path ./pkey
    --account-address 0x1231231212321
```

```python title="migrations/migration_01.cairo"
%lang starknet

@external
func up():
    %{ 
        contract_address = deploy_contract("./build/main.json").contract_address
        
        result = invoke(
            contract_address,
            "initialize",
            {"authority": 123213123123},
            max_fee=10000,
        )
    %}

    return ()
end
```

```cairo title="src/main.cairo"
%lang starknet

@storage_var
func authority() -> (res : felt):
end


@external
func initialize(authority: felt):
    if authority != 0:
        with_attr error_message("Authority has already been set"):
           assert 1 = 0
        end
    end
    
    authority.write(authority)
    return (arg)
end
```