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
    %{ tmp_state["contract"] = deploy_contract("./tests/integration/testing_hooks/basic_contract.cairo") %}
    return ()
end

@view
func test_contract_was_deployed_in_setup_state{
    syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr
}():
    tempvar contract_address

    %{ ids.contract_address = tmp_state["contract"].contract_address %}

    BasicContract.increase_balance(contract_address, 42)
    let (result) = BasicContract.get_balance(contract_address)

    assert result = 42

    # The following hint tries to modify the state for the next test case
    %{ tmp_state["contract"] = None %}

    return ()
end

@view
func test_tmp_state_remains_unchanged_despite_modification_in_test_case_above():
    %{ assert tmp_state["contract"].contract_address is not None %}

    return ()
end
