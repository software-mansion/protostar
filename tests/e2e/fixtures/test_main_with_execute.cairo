%lang starknet
from src.main_with_execute import __execute__

@external
func test_main() {
    let (res) = __execute__();
    assert res = 42;

    return ();
}
