func test_happy_case() {
    %{
        msg_from_l1 = 530437
        contract_address = deploy_contract("src/main.cairo").contract_address
        send_message_to_l2(
            fn_name="existing_handler",
            from_address=123,
            payload=[msg_from_l1],
            to_address=contract_address,
        )
        result = call(contract_address, "get_state")
        assert result == msg_from_l1, "State is updated by the L1 handler"
    %}
    return ();
}
