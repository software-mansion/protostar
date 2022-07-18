%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import get_contract_address
from starkware.starknet.common.syscalls import deploy
from starkware.cairo.common.alloc import alloc
from starkware.cairo.common.uint256 import Uint256

const CONST_VAL = 12234214

@contract_interface
namespace ProxyContract:
    func set_target(new_target : felt):
    end

    func increase_twice(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

namespace test_utils:
    func internal_function{
            syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
        assert 0 = 0
        return ()
    end
end

func internal_function{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    assert 0 = 0
    return ()
end

@external
func test_case1{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    internal_function()
    return ()
end

@view
func test_case2{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    internal_function()
    return ()
end

