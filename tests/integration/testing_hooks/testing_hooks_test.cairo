%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin

@view
func setup_tmp_state():
    %{ tmp_state["contract"] = deploy_contract("./tests/integration/testing_hooks/basic_contract.cairo") %}
    return ()
end

@view
func test_contract_was_deployed_in_setup_state():
    tempvar contract_address = 42

    %{
        assert tmp_state["contract"].contract_address is not None
        tmp_state["contract"] = None
    %}

    return ()
end

@view
func test_tmp_state_remains_unchanged_despite_modification_in_test_case_above():
    tempvar contract_address = 42

    %{ assert tmp_state["contract"].contract_address is not None %}

    return ()
end
