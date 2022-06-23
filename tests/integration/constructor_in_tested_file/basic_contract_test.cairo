%lang starknet
from tests.integration.constructor_in_tested_file.basic_contract import balance, increase_balance

@external
func test_nothing{}():
    return ()
end
