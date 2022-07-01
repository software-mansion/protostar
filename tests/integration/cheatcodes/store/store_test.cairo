%lang starknet
from starkware.starknet.common.syscalls import get_block_number
from starkware.cairo.common.cairo_builtins import HashBuiltin

@contract_interface
namespace BlockNumberContract:
    func get_value() -> (res : felt):
    end

    func get_map_value(key : felt) -> (
            res : felt):
    end
end

# @storage_var
# func target(key: felt) -> (res: felt):
# end


@external
func test_changing_block_number_in_deployed_contract{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    local contract_address

    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/store/block_number_contract.cairo").contract_address
        store("target", 5, None, ids.contract_address)
    %}

    let (bn) = BlockNumberContract.get_value(contract_address)

    assert bn = 5
    return ()
end


@external
func test_changing_block_number_in_deployed_contract_map{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    local contract_address

    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/store/block_number_contract.cairo").contract_address
        store("target_map", 5, [12], ids.contract_address)
    %}

    let (bn) = BlockNumberContract.get_map_value(contract_address, 12)

    assert bn = 5
    return ()
end
