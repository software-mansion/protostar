%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin

@view
func setup_state():
    %{ tmp_state["contract"] = deploy_contract("./tests/integration/testing_hooks/basic_contract.cairo") %}
    return ()
end

@view
func test_contract_was_deployed_in_setup_state():
    tempvar contract_address = 42

    %{ assert tmp_state["contract"].contract_address is not None %}

    return ()
end
