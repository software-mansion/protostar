%lang starknet

@external
func test_fuzz{syscall_ptr : felt*, range_check_ptr}(a, b : felt):
    assert a + b = b + a
    return ()
end
