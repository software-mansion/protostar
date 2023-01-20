from starkware.cairo.common.math import assert_not_zero

func test_mock_call_simple() {
    alloc_locals;

    %{
        addr = deploy_contract("./src/basic.cairo").contract_address
        assert addr != 0
        mock_call(addr, "get_balance", [200])
        result = call(addr, "get_balance")
        assert result == [200]
    %}
    return ();
}

func test_mock_call_with_stop() {
    alloc_locals;

    %{
        addr = deploy_contract("./src/basic.cairo").contract_address
        assert addr != 0
        stop_mock = mock_call(addr, "get_balance", [200])
        result = call(addr, "get_balance")
        assert result == [200]
        stop_mock()
        result = call(addr, "get_balance")
        assert result == [100]
    %}
    return ();
}

func test_mock_call_different_addresses() {
    alloc_locals;

    %{
        addr1 = deploy_contract("./src/basic.cairo").contract_address
        assert addr1 != 0

        addr2 = deploy_contract("./src/basic.cairo").contract_address
        assert addr2 != 0

        stop_mock1 = mock_call(addr1, "get_balance", [200])
        stop_mock2 = mock_call(addr2, "get_balance", [300])

        result = call(addr1, "get_balance")
        assert result == [200]

        result = call(addr2, "get_balance")
        assert result == [300]

        stop_mock1()

        result = call(addr1, "get_balance")
        assert result == [100]

        result = call(addr2, "get_balance")
        assert result == [300]

        stop_mock2()

        result = call(addr1, "get_balance")
        assert result == [100]

        result = call(addr2, "get_balance")
        assert result == [100]


    %}
    return ();
}

func test_mock_call_mock_twice_fail() {
    alloc_locals;

    %{
        addr = deploy_contract("./src/basic.cairo").contract_address
        assert addr != 0
        stop_mock = mock_call(addr, "get_balance", [200])
        stop_mock = mock_call(addr, "get_balance", [300])
    %}
    return ();
}

func test_mock_call_stop_mock_twice_fail() {
    alloc_locals;

    %{
        addr = deploy_contract("./src/basic.cairo").contract_address
        assert addr != 0
        stop_mock = mock_call(addr, "get_balance", [200])
        stop_mock()
        stop_mock()
    %}
    return ();
}

func test_expect_call_with_proxy(){
    %{
        target_addr = deploy_contract("./src/basic.cairo").contract_address
        proxy_addr = deploy_contract("./src/proxy.cairo").contract_address
        invoke(proxy_addr, "set_target", [target_addr])

        mock_call(target_addr, "get_balance", [15])
        assert call(target_addr, "get_balance") == [15]
        assert call(proxy_addr, "get_balance") == [15]
        
        mock_call(proxy_addr, "get_balance", [40])
        assert call(target_addr, "get_balance") == [15]
        assert call(proxy_addr, "get_balance") == [40]
    %}

    return ();
}
