%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin

@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@external
func __setup__():
    %{ context.contract_address = deploy_contract("./tests/integration/testing_hooks/basic_contract.cairo").contract_address %}
    return ()
end

func before_each{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (
        contract_address : felt):
    alloc_locals
    local contract_address
    %{ ids.contract_address = context.contract_address %}
    BasicContract.increase_balance(contract_address, 1)
    return (contract_address)
end

@external
func test_contract_was_deployed_in_setup{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    let (contract_address) = before_each()

    BasicContract.increase_balance(contract_address, 41)
    let (result) = BasicContract.get_balance(contract_address)

    assert result = 42
    return ()
end

@external
func test_contract_was_deployed_in_setup_is_not_affected_by_the_previous_test_case{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    let (contract_address) = before_each()

    BasicContract.increase_balance(contract_address, 41)
    let (result) = BasicContract.get_balance(contract_address)

    assert result = 42
    return ()
end
