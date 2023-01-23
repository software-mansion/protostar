from starkware.cairo.common.math import assert_not_zero

func test_deploying_contract_by_name(){
    alloc_locals;
    local deployed_contract_address;

    %{ ids.deployed_contract_address = deploy_contract("main").ok.contract_address %}

    assert_not_zero(deployed_contract_address);
    return ();
}

func test_deploying_contract(){
    alloc_locals;
    local deployed_contract_address;

    %{ ids.deployed_contract_address = deploy_contract("./src/basic.cairo").ok.contract_address %}

    assert_not_zero(deployed_contract_address);
    return ();
}

func test_deploying_contract_with_constructor(){
    alloc_locals;
    local deployed_contract_address;


    %{ ids.deployed_contract_address = deploy_contract("./src/basic_with_constructor.cairo", [123]).ok.contract_address %}

    assert_not_zero(deployed_contract_address);
    return ();
}