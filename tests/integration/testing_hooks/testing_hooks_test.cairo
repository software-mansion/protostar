%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin

@view
func setup_state():
    %{ state["contract"] = deploy_contract("./src/main.cairo") %}
    return ()
end

@view
func test_contract_was_deployed_in_setup_state():
    tempvar contract_address

    %{ assert state["contract"].contract_address is not None %}

    return ()
end
