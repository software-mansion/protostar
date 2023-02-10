func test_happy_path() {
    %{
        number_provider_address_1 = deploy_contract("number_provider").ok.contract_address
        number_provider_address_2 = deploy_contract("number_provider").ok.contract_address
        number_provider_proxy_address = deploy_contract("number_provider_proxy").ok.contract_address

        assert call(number_provider_proxy_address, "get_number", [number_provider_address_1]).ok == 1
        assert call(number_provider_proxy_address, "get_number", [number_provider_address_2]).ok == 1

        mock_call(number_provider_address_1, "get_number", [42])

        assert call(number_provider_proxy_address, "get_number", [number_provider_address_1]).ok == 42
        assert call(number_provider_proxy_address, "get_number", [number_provider_address_2]).ok == 1
    %}
    return ();
}

func test_fail_when_call_was_mocked_twice() {
    %{
        assert mock_call(123, "_", [42]).err_code == 0
        assert mock_call(123, "_", [24]).err_code == 0
        assert mock_call(123, "get_number", [42]).err_code == 0
        assert mock_call(123, "get_number", [42]).err_code != 0
    %}
    return ();
}
