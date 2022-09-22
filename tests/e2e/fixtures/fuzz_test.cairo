%lang starknet

@external
func test_deploy_contract_simplified(a : felt) {
    assert a = 5;
    assert 3 = 3;
    return ();
}
