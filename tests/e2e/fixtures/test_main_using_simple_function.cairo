%lang starknet
from src.main import my_func

@external
func test_my_func{syscall_ptr : felt*, range_check_ptr}():
    let (res) = my_func()
    assert res = 42
    return ()
end
