%lang starknet
from tests.integration.compilation.basic_contract import balance, increase_balance

@external
func test_nothing{}() {
    return ();
}
