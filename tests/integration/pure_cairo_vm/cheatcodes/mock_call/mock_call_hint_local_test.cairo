func test_happy_path() {
    %{
        number_provider_address_1 = deploy_contract("number_provider").ok.contract_address
        number_provider_address_2 = deploy_contract("number_provider").ok.contract_address
        number_provider_proxy_address = deploy_contract("number_provider_proxy").ok.contract_address

        assert call(number_provider_proxy_address, "get_number", [number_provider_address_1]).ok == [1]
        assert call(number_provider_proxy_address, "get_number", [number_provider_address_2]).ok == [1]

        mock_call(number_provider_address_1, "get_number", [42])

        assert call(number_provider_proxy_address, "get_number", [number_provider_address_1]).ok == [42]
        assert call(number_provider_proxy_address, "get_number", [number_provider_address_2]).ok == [1]
    %}
    return ();
}

func test_mocking_call_twice() {
    %{
        number_provider_address = deploy_contract("number_provider").ok.contract_address
        number_provider_proxy_address = deploy_contract("number_provider_proxy").ok.contract_address

        mock_call(number_provider_address, "get_number", [21])
        mock_call(number_provider_address, "get_number", [37])

        assert call(number_provider_proxy_address, "get_number", [number_provider_address]).ok == [37]
    %}
    return ();
}
