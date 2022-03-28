%lang starknet

from src.main import main

@external
func test_main_cairo{syscall_ptr : felt*, range_check_ptr}():
    let (r) = main(3,2)
    assert r = 5 
    return ()
end
