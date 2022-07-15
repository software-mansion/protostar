%lang starknet
from starkware.starknet.common.syscalls import get_block_number, get_contract_address
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

    func get_map_value(key : felt) -> (res : felt):
    end

    func get_map_value_struct_key(key : Key) -> (res : felt):
    end

    func get_map_value_struct_val(key : felt) -> (res : Value):
    end

    func get_map_value_complex_key(a : felt, b : felt) -> (res : felt):
    end
end

@storage_var
func target_map_complex_key(a : felt, b : felt) -> (res : Value):
end

@external
func test_load_in_user_contract{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        ):
    alloc_locals
    local contract_address
    local value
    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/load/block_number_contract.cairo").contract_address
        store(ids.contract_address, "target", [5])
        ids.value = load(ids.contract_address, "target", "felt")[0]
    %}

    let (bn) = BlockNumberContract.get_value(contract_address)

    assert bn = value
    return ()
end

@external
func test_load_map_in_user_contract{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    local contract_address
    local value
    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/load/block_number_contract.cairo").contract_address
        store(ids.contract_address, "target_map", [5], key=[12])
        ids.value = load(ids.contract_address, "target_map", "felt", key=[12])[0]
    %}

    let (bn) = BlockNumberContract.get_map_value(contract_address, 12)

    assert bn = value
    return ()
end

@external
func test_load_map_complex_key_in_user_contract{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    local contract_address
    local value
    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/load/block_number_contract.cairo").contract_address
        store(ids.contract_address, "target_map_complex_key", [5], key=[1,2])
        ids.value = load(ids.contract_address, "target_map_complex_key", "felt", key=[1,2])[0]
    %}

    let (bn) = BlockNumberContract.get_map_value_complex_key(contract_address, 1, 2)

    assert bn = 5
    return ()
end

@external
func test_load_map_struct_key_in_user_contract{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    local contract_address
    local value
    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/load/block_number_contract.cairo").contract_address
        store(ids.contract_address, "target_map_struct_key", [5], key=[1,2])
        ids.value = load(ids.contract_address, "target_map_struct_key", "felt", key=[1,2])[0]
    %}
    let key_v = Key(a=1, b=2)
    let (bn) = BlockNumberContract.get_map_value_struct_key(contract_address, key_v)
    assert value = bn
    return ()
end

@external
func test_load_map_struct_val_in_user_contract{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    local contract_address
    local value : Value
    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/load/block_number_contract.cairo").contract_address
        store(ids.contract_address, "target_map_struct_val", [5,10], key=[1])
        value_arr = load(ids.contract_address, "target_map_struct_val", "Value", key=[1])
        ids.value.a = value_arr[0]
        ids.value.b = value_arr[1]
    %}

    let (bn) = BlockNumberContract.get_map_value_struct_val(contract_address, 1)

    assert value.a = bn.a
    assert value.b = bn.b
    return ()
end

@external
func test_map_load_local{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    let (contract_address) = get_contract_address()
    local value : Value
    %{
        store(ids.contract_address, "target_map_complex_key", [1, 2], key=[5, 6])
        value_arr = load(ids.contract_address, "target_map_complex_key", "Value", key=[5,6])
        ids.value.a = value_arr[0]
        ids.value.b = value_arr[1]
    %}
    let (bn) = target_map_complex_key.read(5, 6)

    assert value.a = bn.a
    assert value.b = bn.b
    return ()
end

@external
func test_missing_type_name{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    alloc_locals
    # assert in load_test.py
    let (contract_address) = get_contract_address()
    local value : Value
    %{
        store(ids.contract_address, "target_map_complex_key", [1, 2], key=[5, 6])
        value_arr = load(ids.contract_address, "target_map_complex_key", "ValueB", key=[5,6])
    %}
    return ()
end
