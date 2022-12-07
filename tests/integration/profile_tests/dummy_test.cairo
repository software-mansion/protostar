%lang starknet

@external
func test_dummy() {
    assert 5 = 5;
    return ();
}
