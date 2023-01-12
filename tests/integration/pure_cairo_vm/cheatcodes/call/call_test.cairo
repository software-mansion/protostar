from starkware.cairo.common.math import assert_not_zero

func test_call_simple() {
    alloc_locals;
    local deployed_contract_address;

    %{ ids.deployed_contract_address = deploy_contract("./src/basic.cairo").contract_address %}
    assert_not_zero(deployed_contract_address);

    %{
        result = call(ids.deployed_contract_address, "get_balance")
        assert result == [100]
    %}
    return ();
}

func test_call_not_mutating_state() {
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

func test_call_named_args() {
    alloc_locals;
    local deployed_contract_address;

    %{ ids.deployed_contract_address = deploy_contract("./src/basic.cairo").contract_address %}
    assert_not_zero(deployed_contract_address);

    %{ call(ids.deployed_contract_address, "increase_balance", {"amount": 50}) %}
    return ();
}

func test_call_named_args_invalid_fail() {
    alloc_locals;
    local deployed_contract_address;

    %{ ids.deployed_contract_address = deploy_contract("./src/basic.cairo").contract_address %}
    assert_not_zero(deployed_contract_address);

    %{ call(ids.deployed_contract_address, "increase_balance", {"xxx": 50}) %}
    return ();
}
