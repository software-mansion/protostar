# `roll`

```python
def roll(blk_number: int, target_contract_address: Optional[int] = None) -> Callable[[], None]: ...
```

Changes a block number until the returned function is called. If `target_contract_address` is specified, `roll` affects only the contract with the specified address. Otherwise, `roll` affects the current contract.

```cairo title="Roll cheatcode changes the value returned by get_block_number"
%lang starknet
from starkware.starknet.common.syscalls import get_block_number

@external
func test_changing_block_number{syscall_ptr: felt*}() {
    %{ stop_roll = roll(123) %}
    let (bn) = get_block_number();
    assert bn = 123;
    %{ stop_roll() %}

    let (bn2) = get_block_number();
    %{ ids.bn2 != 123 %}

    return ();
}
```
