

func setup_a(){
    %{ context.contract_address = deploy_contract("./src/main.cairo").contract_address %}
    return ();
}

func test_a(){
    alloc_locals;
    local initial_balance;

    %{ ids.initial_balance = call(context.contract_address, "get_balance")[0] %}
    assert initial_balance = 100;

    local increased_balance;
    %{
        invoke(context.contract_address, "increase_balance", [100])
        ids.increased_balance =  call(context.contract_address, "get_balance")[0]

    %}
    assert increased_balance = 200;

    return ();
}

func test_b_doesnt_leak_from_a_setup(){
    alloc_locals;
    local contract_deployed;

    %{
        ids.contract_deployed = 1 if hasattr(context, "contract_address") else 0
    %}
    assert contract_deployed = 0;
    return ();
}