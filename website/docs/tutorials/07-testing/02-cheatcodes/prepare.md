# `prepare`
```python
def prepare(declared: DeclaredContract, constructor_calldata: Optional[Union[List[int], Dict]]] = None) -> PreparedContract:

class PreparedContract:
    constructor_calldata: List[int]
    contract_address: int
    class_hash: int
```
Prepares contract for deployment given `DeclaredContract` and constructor_calldata. The cheatcode is useful when you want to know contract address before deploying it to affect constructor with a targeted cheatcode. Example:

```
@external
func test_prank_constructor{syscall_ptr : felt*, range_check_ptr}():
    %{
        declared = declare("path/to/contract.cairo")
        prepared = prepare(declared, [1,2,3])
        start_prank(111, target_contract_address=prepared.contract_address)

        # constructor will be affected by prank
        deploy(prepared)
    %}
    return ()
end

```
:::info
You can prepare multiple contracts from one `DeclaredContract`.
:::

:::tip
You can provide `constructor_calldata` as a dictionary to leverage [data transformer](README.md#data-transformer).
:::
