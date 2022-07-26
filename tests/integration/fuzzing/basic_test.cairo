%lang starknet

from starkware.cairo.common.math import assert_nn

@external
func test_fuzz{syscall_ptr : felt*, range_check_ptr}(a, b : felt):
    assert a + b = b + a
    return ()
end

@external
func test_fails_if_big{syscall_ptr : felt*, range_check_ptr}(a, b, c):
    assert_nn(a)
    return ()
end
