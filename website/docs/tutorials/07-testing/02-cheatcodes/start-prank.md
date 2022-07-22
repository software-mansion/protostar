# `start_prank`

```python
def start_prank(caller_address: int, target_contract_address: Optional[int] = None) -> Callable: ...
```

Changes a caller address returned by `get_caller_address()` until the returned callable is called. If `target_contract_address` is specified, `start_prank` affects only the contract with the specified address. Otherwise, `start_prank` affects the current contract.

## In unit tests
```cairo title="Local assert passes"

@external
func test_remote_prank{syscall_ptr : felt*, range_check_ptr}():
    %{ stop_prank_callable = start_prank(123) %}

    let (caller_addr) = get_caller_address()
    # Does not raise error
    assert caller_addr = 123

    %{ stop_prank_callable() %}
    return ()
end
``` 
## In integration tests
```cairo title="./pranked_contract.cairo"
%lang starknet

from starkware.starknet.common.syscalls import (get_caller_address)

@external
func assert_pranked{syscall_ptr : felt*}():
    let (caller_addr) = get_caller_address()
    with_attr error_message("Not pranked!"):
        assert caller_addr = 123
    end
    return ()
end
```
```cairo title="Remote assert passes"
@contract_interface
namespace Pranked:
    func assert_pranked() -> ():
    end
end

@external
func test_remote_prank{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local contract_address : felt
    %{ 
        ids.contract_address = deploy_contract("./pranked_contract.cairo").contract_address 
        stop_prank_callable = start_prank(123, target_contract_address=ids.contract_address)
    %}
    # Does not raise error
    Pranked.assert_pranked(contract_address=contract_address)
    %{ stop_prank_callable() %}
    return ()
end
``` 
