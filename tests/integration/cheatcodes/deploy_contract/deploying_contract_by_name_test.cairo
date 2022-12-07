%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin

@contract_interface
namespace BasicContract {
    func increase_balance(amount: felt) {
    }

    func get_balance() -> (res: felt) {
    }
}

@external
func test_deploy_contract_by_name{syscall_ptr: felt*, range_check_ptr}() {
    alloc_locals;

    local contract_address: felt;
    %{
        deployed = deploy_contract("main")
        ids.contract_address = deployed.contract_address
    %}

    BasicContract.increase_balance(contract_address, 5);
    let (res) = BasicContract.get_balance(contract_address);
    assert res = 5;
    return ();
}
