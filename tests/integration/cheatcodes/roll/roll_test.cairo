%lang starknet
from starkware.starknet.common.syscalls import get_block_number

@external
func test_changing_block_number{syscall_ptr: felt*}() {
    %{ stop_roll = roll(123) %}
    let (bn) = get_block_number();
    assert bn = 123;
    %{ stop_roll() %}

    let (bn2) = get_block_number();
    %{ ids.bn2 != 123 %}

    return ();
}

@contract_interface
namespace BlockNumberContract {
    func get_my_block_number() -> (res: felt) {
    }
}

@external
func test_changing_block_number_in_deployed_contract{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;
    local contract_address;

    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/roll/block_number_contract.cairo").contract_address
        stop_roll = roll(123, ids.contract_address)
    %}
    let (bn) = BlockNumberContract.get_my_block_number(contract_address);
    assert bn = 123;
    let (local_block_number) = get_block_number();
    %{
        assert ids.local_block_number != 123
        stop_roll()
    %}

    let (bn2) = BlockNumberContract.get_my_block_number(contract_address);
    %{ assert ids.bn2 != 123 %}

    return ();
}
