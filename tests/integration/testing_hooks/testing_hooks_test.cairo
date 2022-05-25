%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin

func setup_state():
    %{ contract = deploy_contract("./src/main.cairo") %}
    return ()
end

@view
func test_contract_was_deployed_in_setup_state():
    tempvar contract_address

    %{ assert contract.contract_address is not None %}

    return ()
end
