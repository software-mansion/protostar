from starkware.cairo.common.math import assert_not_zero

func test_warp(){
    alloc_locals;
    local deployed_contract_address;

    %{
        ids.deployed_contract_address = deploy_contract("main").contract_address
        warp(123, ids.deployed_contract_address)
    %}

    assert_not_zero(deployed_contract_address);
    return ();
}