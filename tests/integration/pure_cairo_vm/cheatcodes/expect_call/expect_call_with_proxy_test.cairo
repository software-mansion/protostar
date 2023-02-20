func test_expect_call_with_proxy_simple() {
    %{
        target_addr = deploy_contract("./src/basic.cairo").ok.contract_address
        proxy_addr = deploy_contract("./src/proxy.cairo").ok.contract_address

        invoke(proxy_addr, "set_target", [target_addr])

        expect_call(proxy_addr, "increase_twice", [50])
        call(proxy_addr, "increase_twice", [50])
    %}

    return ();
}

func test_expect_call_with_proxy_deeper() {
    %{
        target_addr = deploy_contract("./src/basic.cairo").ok.contract_address
        proxy_addr = deploy_contract("./src/proxy.cairo").ok.contract_address

        invoke(proxy_addr, "set_target", [target_addr])

        expect_call(proxy_addr, "increase_twice", [50])
        expect_call(target_addr, "increase_balance", [50])
        call(proxy_addr, "increase_twice", [50])
    %}

    return ();
}
