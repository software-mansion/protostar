func __setup__(){
    %{ context.contract_address = deploy_contract("./src/main.cairo").contract_address %}
    return ();
}


func test_setup_with_deployment(){
    alloc_locals;
    local initial_balance;

    %{ ids.initial_balance = call(context.contract_address, "get_balance")[0] %}
    assert initial_balance = 100;

    return ();
}