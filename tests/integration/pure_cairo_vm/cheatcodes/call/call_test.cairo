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

func test_call_with_proxy_simple(){
    alloc_locals;

    %{
        target_addr = deploy_contract("./src/basic.cairo").contract_address
        proxy_addr = deploy_contract("./src/proxy.cairo").contract_address

        invoke(proxy_addr, "set_target", [target_addr])

        assert call(proxy_addr, "get_balance") == [100]
        call(proxy_addr, "increase_twice", [50])
        call(target_addr, "increase_balance", [50])
        assert call(proxy_addr, "get_balance") == [100]
    %}


    return ();
}

func test_call_with_proxy_named_args_success(){
    alloc_locals;

    %{
        target_addr = deploy_contract("./src/basic.cairo").contract_address
        proxy_addr = deploy_contract("./src/proxy.cairo").contract_address

        invoke(proxy_addr, "set_target", [target_addr])

        call(proxy_addr, "increase_twice", {"amount": 50})
    %}

    return ();
}

func test_call_with_proxy_named_args_fail(){
    alloc_locals;

    %{
        target_addr = deploy_contract("./src/basic.cairo").contract_address
        proxy_addr = deploy_contract("./src/proxy.cairo").contract_address

        invoke(proxy_addr, "set_target", [target_addr])

        call(proxy_addr, "increase_twice", {"amount_": 50})
    %}

    return ();
}
