from starkware.cairo.common.math import assert_not_zero

func test_invoke_without_transformation(){
    alloc_locals;
    local deployed_contract_address;

    %{ ids.deployed_contract_address = deploy_contract("./src/basic.cairo").contract_address %}
    assert_not_zero(deployed_contract_address);

    local balance;
    %{
        ids.balance = call(ids.deployed_contract_address, "get_balance")[0]
    %}
    assert balance = 100;

    local new_balance;
    %{ invoke(ids.deployed_contract_address, "increase_balance", {"amount": 123}) %}
    %{
        ids.new_balance = call(ids.deployed_contract_address, "get_balance")[0]
    %}
    assert new_balance = 223;

    %{ invoke(ids.deployed_contract_address, "increase_balance", [123]) %}
    return ();
}


func test_invoke_with_transformation(){
    alloc_locals;
    local deployed_contract_address;


    %{ ids.deployed_contract_address = deploy_contract("./src/basic.cairo").contract_address %}
    assert_not_zero(deployed_contract_address);

    local balance;
    %{
        ids.balance = call(ids.deployed_contract_address, "get_balance")[0]
    %}
    assert balance = 100;

    local new_balance;
    %{ invoke(ids.deployed_contract_address, "increase_balance", {"amount": 123}) %}
    %{
        ids.new_balance = call(ids.deployed_contract_address, "get_balance")[0]
    %}
    assert new_balance = 223;

    return ();
}
