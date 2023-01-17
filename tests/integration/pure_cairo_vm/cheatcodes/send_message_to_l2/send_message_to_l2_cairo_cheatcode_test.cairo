func test_happy_path() {
    %{
        msg_from_l1 = 530437
        contract_address = deploy_contract("src/main.cairo").contract_address
        send_message_to_l2(
            function_name="existing_handler",
            from_address=123,
            payload=[msg_from_l1],
            to_address=contract_address,
        )
        result = call(contract_address, "get_state")
        assert [msg_from_l1] == result, f"Expected '{[msg_from_l1]}', but got: '{result}'"
    %}
    return ();
}

func test_data_transformer() {
    %{
        msg_from_l1 = 530437
        contract_address = deploy_contract("src/main.cairo").contract_address
        send_message_to_l2(
            function_name="existing_handler",
            from_address=123,
            payload={"value": msg_from_l1},
            to_address=contract_address,
        )
        result = call(contract_address, "get_state")
        assert [msg_from_l1] == result, f"Expected '{[msg_from_l1]}', but got: '{result}'"
    %}
    return ();
}
