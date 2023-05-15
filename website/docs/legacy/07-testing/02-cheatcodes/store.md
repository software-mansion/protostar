# `store`
```python
def store(target_contract_address: int, variable_name: str, value: List[int], key: Optional[List[int]] = None):
```
Updates storage variable with name `variable_name` and given key to `value` of a contract with `target_contract_address`.
Example:

```cairo title="./src/contract.cairo"
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import get_block_number

struct Value {
    a: felt,
    b: felt,
}

@storage_var
func store_val(a: felt, b: felt) -> (res: Value) {
}

@view
func get_value{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    a: felt, b: felt
) -> (res: Value) {
    let (val) = store_val.read(a, b);
    return (val,);
}
```

```cairo title="./test/test_store.cairo"
%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin
from src.contract import Value

@contract_interface
namespace Contract {
    func get_value(a: felt, b: felt) -> (res: Value) {
    }
}

@external
func test_store{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    alloc_locals;
    local contract_address;

    %{
        ids.contract_address = deploy_contract("./src/contract.cairo").contract_address
        store(ids.contract_address, "store_val", [4, 3], key=[1,2])
    %}

    let (bn) = Contract.get_value(contract_address, 1, 2);

    assert 4 = bn.a;
    assert 3 = bn.b;
    return ();
}
```

:::warning
You have to provide `value` and `key` as list of ints. In the future Data Transformer will be supported.
:::

:::warning
There is no type checking for `variable_name`, `value`, `key`, make sure you provided values correctly.
:::

:::tip
`key` is a list of arguments because Cairo `@storage_var` maps any number of felt arguments to any number of felt values.
:::
