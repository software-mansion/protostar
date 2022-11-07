# `load`
```python
def load(
    target_contract_address: int,
    variable_name: str,
    variable_type: str,
    key: list[int] | None = None
) -> list[int]:
```
Loads storage variable with name `variable_name` and given `key` and `variable_type` from a contract with `target_contract_address`.
`variable_type` is provided as a string representation of type name.
Example:

```cairo title="./src/contract.cairo"
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

struct Value {
    a: felt,
    b: felt,
}

@storage_var
func store_val(a: felt, b: felt) -> (res: Value) {
}

@storage_var
func store_felt() -> (res: felt) {
}
```

```cairo title="./test/test_store.cairo"
%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin

@external
func test_store{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    alloc_locals;
    local contract_address;
    %{
        ids.contract_address = deploy_contract("./src/contract.cairo").contract_address
        felt_val = load(ids.contract_address, "store_felt", "felt")
        assert felt_val == [0]

        value_val = load(ids.contract_address, "store_val", "Value", key=[1,2])
        assert value_val == [0, 0]
    %}
    return ();
}
```

:::warning
You have to provide `key` as list of ints. In the future Data Transformer will be supported.
:::

:::warning
There is no type checking for `variable_name`, `key`, `variable_type` make sure you provided values correctly.
:::

:::tip
`key` is a list of arguments because Cairo `@storage_var` maps any number of felt arguments to any number of felt values.
:::
