%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin

@contract_interface
namespace BasicContract:
    func increase_balance(amount : felt):
    end

    func get_balance() -> (res : felt):
    end
end

@view
func setup_state():
    %{ context.contract_address = deploy_contract("./tests/integration/testing_hooks/basic_contract.cairo").contract_address %}
    return ()
end

@view
func test_contract_was_deployed_in_setup_state{
        syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    tempvar contract_address

    %{ ids.contract_address = context.contract_address %}

    BasicContract.increase_balance(contract_address, 42)
    let (result) = BasicContract.get_balance(contract_address)

    assert result = 42

    return ()
end
