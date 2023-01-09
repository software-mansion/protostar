from starkware.cairo.common.math import assert_not_zero

func test_invoke_without_transformation(){
    alloc_locals;
    local deployed_contract_address;

    %{ ids.deployed_contract_address = deploy_contract("./src/basic.cairo").contract_address %}
    assert_not_zero(deployed_contract_address);

    %{ invoke(ids.deployed_contract_address, "increase_balance", [123]) %}
    return ();
}


func test_invoke_with_transformation(){
    alloc_locals;
    local deployed_contract_address;

    %{ ids.deployed_contract_address = deploy_contract("./src/basic.cairo").contract_address %}
    assert_not_zero(deployed_contract_address);

    %{ invoke(ids.deployed_contract_address, "increase_balance", {"amount": 123}) %}
    return ();
}
