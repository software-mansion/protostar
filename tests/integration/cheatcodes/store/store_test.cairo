%lang starknet
from starkware.starknet.common.syscalls import get_block_number
from starkware.cairo.common.cairo_builtins import HashBuiltin

struct Key:
    member a : felt
    member b : felt
end

struct Value:
    member a : felt
    member b : felt
end

@contract_interface
namespace BlockNumberContract:
    func get_value() -> (res : felt):
    end

    func get_map_value(key : felt) -> (
            res : felt):
    end

    func get_map_value_struct_key(key : Key) -> (res : felt):
    end

    func get_map_value_struct_val(key : felt) -> (res : Value):
    end

    func get_map_value_complex_key(a: felt, b: felt) -> (res : felt):
    end
end


@external
func test_store_in_deployed_contract{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    local contract_address

    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/store/block_number_contract.cairo").contract_address
        store(ids.contract_address, "target", 5)
    %}

    let (bn) = BlockNumberContract.get_value(contract_address)

    assert bn = 5
    return ()
end


@external
func test_store_map_in_deployed_contract{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    local contract_address

    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/store/block_number_contract.cairo").contract_address
        store(ids.contract_address, "target_map", 5, key=[12])
    %}

    let (bn) = BlockNumberContract.get_map_value(contract_address, 12)

    assert bn = 5
    return ()
end

@external
func test_store_map_complex_key_in_deployed_contract{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    local contract_address

    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/store/block_number_contract.cairo").contract_address
        store(ids.contract_address, "target_map", 5, key=[1,2])
    %}

    let (bn) = BlockNumberContract.get_map_value_complex_key(contract_address, 1, 2)

    assert bn = 5
    return ()
end

@external
func test_store_map_struct_key_in_deployed_contract{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    local contract_address

    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/store/block_number_contract.cairo").contract_address
        store(ids.contract_address, "target_map", 5, key=[1,2])
    %}

    let key_v = Key(
        a=1,
        b=2,
    )

    let (bn) = BlockNumberContract.get_map_value_struct_key(contract_address, key_v)

    assert bn = 5
    return ()
end


@external
func test_store_map_struct_val_in_deployed_contract{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    local contract_address

    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/store/block_number_contract.cairo").contract_address
        store(ids.contract_address, "target_map", [5,10], key=[1])
    %}

    let (bn) = BlockNumberContract.get_map_value_struct_val(contract_address, 1)

    assert 5 = bn.a
    assert 10 = bn.b
    return ()
end

## key struct
## value struct
## complex key
## transformer complex
# redirect local

# @external
# func test_map_in_deployed_contract{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
#     alloc_locals
#     local contract_address

#     %{
#         ids.contract_address = deploy_contract("./tests/integration/cheatcodes/store/block_number_contract.cairo").contract_address
#         store("target", 5, None, ids.contract_address)
#     %}

#     let (bn) = BlockNumberContract.get_value(contract_address)

#     assert bn = 5
#     return ()
# end
