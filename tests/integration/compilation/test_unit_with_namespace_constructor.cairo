%lang starknet
from tests.integration.compilation.namespace_constructor import balance, increase_balance

@external
func test_nothing{}() {
    return ();
}
