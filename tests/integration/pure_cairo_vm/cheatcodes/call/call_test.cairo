from starkware.cairo.common.math import assert_not_zero

func test_call(){
    alloc_locals;
    local deployed_contract_address;

    %{ ids.deployed_contract_address = deploy_contract("./src/basic.cairo").contract_address %}
    assert_not_zero(deployed_contract_address);

    %{
        result = call(ids.deployed_contract_address, "get_balance")
        assert result == [100]
        call(ids.deployed_contract_address, "increase_balance", [50])
        result = call(ids.deployed_contract_address, "get_balance")
        assert result == [100]
    %}
    return ();
}
