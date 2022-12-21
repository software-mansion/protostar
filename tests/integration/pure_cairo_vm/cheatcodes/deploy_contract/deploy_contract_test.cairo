// TODO: Replace ending assertions with contract interaction when made possible via "call" cheat
func test_deploying_contract(){
    alloc_locals;
    local deployed_contract_address;

    %{ ids.deployed_contract_address = deploy_contract("./src/basic.cairo").contract_address %}

    assert deployed_contract_address = 1144079294511026487316353835258546826856691918246830935554569370672270626366;
    return ();
}

func test_deploying_contract_with_constructor(){
    alloc_locals;
    local deployed_contract_address;


    %{ ids.deployed_contract_address = deploy_contract("./src/basic_with_constructor.cairo", [123]).contract_address %}
    assert deployed_contract_address = 3197174707164068245127870226255417011006457516922376712780131249482193907169;
    return ();
}