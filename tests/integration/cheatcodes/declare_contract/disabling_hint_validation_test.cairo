%lang starknet
from tests.integration.cheatcodes.declare_contract.contract_with_invalid_hint import main

@view
func test_invalid_hint_in_deployed_contract():
    %{ deploy_contract("tests/integration/cheatcodes/declare_contract/disabling_hint_validation_test.cairo") %}
    # assert in the pytest file
    return ()
end
