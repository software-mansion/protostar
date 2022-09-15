# `warp`

```python
def warp(blk_timestamp: int, target_contract_address: Optional[int] = None) -> Callable[[], None]: ...
```

Changes a block timestamp until the returned function is called. If `target_contract_address` is specified, `warp` affects only the contract with the specified address. Otherwise, `warp` affects the current contract.

```cairo title="Warp cheatcode changes the value returned by get_block_timestamp"
%lang starknet

from starkware.starknet.common.syscalls import get_block_timestamp

@external
func test_changing_timestamp{syscall_ptr: felt*}() {
    %{ stop_warp = warp(321) %}
    let (bt) = get_block_timestamp();
    assert bt = 321;

    %{ stop_warp() %}
    let (bt2) = get_block_timestamp();
    %{ assert ids.bt2 != 321 %}
    return ();
}
```
