%lang starknet

@view
func test_invalid_hint_in_deployed_contract():
    %{ deploy_contract("./src/contract_with_invalid_hint.cairo") %}
    return ()
end
