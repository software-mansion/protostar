from starkware.cairo.common.math import assert_not_zero

func test_expect_call_success(){
    %{
        addr = deploy_contract("./src/basic.cairo").contract_address
        assert addr != 0
        stop_expect = expect_call(addr, "increase_balance", [50])
        call(addr, "increase_balance", [50])
    %}
    return ();
}


func test_expect_call_before_stop_success(){
    %{
        addr = deploy_contract("./src/basic.cairo").contract_address
        assert addr != 0
        stop_expect = expect_call(addr, "increase_balance", [50])
        call(addr, "increase_balance", [50])
        stop_expect()
    %}
    return ();
}

func test_expect_call_wrong_arg_fail(){
    %{
        addr = deploy_contract("./src/basic.cairo").contract_address
        assert addr != 0
        stop_expect = expect_call(addr, "increase_balance", [51])
        call(addr, "increase_balance", [50])
    %}
    return ();
}

func test_expect_call_after_stop_fail(){
    %{
        addr = deploy_contract("./src/basic.cairo").contract_address
        assert addr != 0
        stop_expect = expect_call(addr, "increase_balance", [50])
        stop_expect()
        call(addr, "increase_balance", [50])
    %}
    return ();
}

func test_expect_call_wrong_function_fail(){
    %{
        addr = deploy_contract("./src/basic.cairo").contract_address
        assert addr != 0
        stop_expect = expect_call(addr, "increase_balance", [50])
        call(addr, "increase_balance_double", [50])
    %}
    return ();
}

func test_expect_call_invalid_function_name_fail(){
    %{
        addr = deploy_contract("./src/basic.cairo").contract_address
        assert addr != 0
        stop_expect = expect_call(addr, "increase_balancee", [50])
        call(addr, "increase_balance", [50])
    %}
    return ();
}

func test_expect_call_with_proxy_simple(){
    %{
        target_addr = deploy_contract("./src/basic.cairo").contract_address
        proxy_addr = deploy_contract("./src/proxy.cairo").contract_address

        invoke(proxy_addr, "set_target", [target_addr])
        
        expect_call(proxy_addr, "increase_twice", [50])
        call(proxy_addr, "increase_twice", [50])
    %}

    return ();
}

func test_expect_call_with_proxy_deeper(){
    %{
        target_addr = deploy_contract("./src/basic.cairo").contract_address
        proxy_addr = deploy_contract("./src/proxy.cairo").contract_address

        invoke(proxy_addr, "set_target", [target_addr])
        
        expect_call(proxy_addr, "increase_twice", [50])
        expect_call(target_addr, "increase_balance", [50])
        call(proxy_addr, "increase_twice", [50])
    %}

    return ();
}
