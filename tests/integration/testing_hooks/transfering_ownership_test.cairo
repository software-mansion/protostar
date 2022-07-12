%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import get_contract_address

@contract_interface
namespace Ownable:
    func transferOwnership(new_owner : felt):
    end

    func owner() -> (owner : felt):
    end
end

@external
func __setup__{syscall_ptr : felt*}():
    let (contract_address) = get_contract_address()
    %{ context.ownable_address = deploy_contract("./tests/data/cairo_contracts/tests/mocks/Ownable.cairo", [ids.contract_address]).contract_address %}

    return ()
end

func change_ownership{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (
        ownable_address : felt):
    alloc_locals
    local ownable_address

    %{ ids.ownable_address = context.ownable_address %}

    Ownable.transferOwnership(ownable_address, 0x42)

    let (owner) = Ownable.owner(ownable_address)

    return (ownable_address)
end

@external
func test_transfering_ownership{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        ):
    let (ownable_address) = change_ownership()
    let (owner) = Ownable.owner(ownable_address)
    assert owner = 0x42
    return ()
end

@external
func test_transfering_ownership_again{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    let (ownable_address) = change_ownership()
    let (owner) = Ownable.owner(ownable_address)
    assert owner = 0x42
    return ()
end
