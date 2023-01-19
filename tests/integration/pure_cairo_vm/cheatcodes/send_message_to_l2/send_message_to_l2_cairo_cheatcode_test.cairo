func test_happy_path() {
    %{
        msg_from_l1 = 530437
        contract_address = deploy_contract("tests/integration/pure_cairo_vm/cheatcodes/send_message_to_l2/external_contract_with_l1_handler.cairo").contract_address
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
        contract_address = deploy_contract("tests/integration/pure_cairo_vm/cheatcodes/send_message_to_l2/external_contract_with_l1_handler.cairo").contract_address
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

func test_other_cheatcodes_impact_l1_handler() {
    %{
        contract_address = deploy_contract("tests/integration/pure_cairo_vm/cheatcodes/send_message_to_l2/external_contract_with_l1_handler.cairo").contract_address
        fake_block_timestamp = 321
        warp(contract_address, fake_block_timestamp)
        send_message_to_l2(
            function_name="on_l1_msg_set_block_timestamp",
            from_address=123,
            to_address=contract_address,
        )
        result = call(contract_address, "get_state")
        assert [fake_block_timestamp] == result, f"Expected '{[fake_block_timestamp]}', but got: '{result}'"
    %}

    return ();
}

func test_other_cheatcodes_impact_contracts_called_from_l1_handler() {
    %{
        tester_address = deploy_contract("tests/integration/pure_cairo_vm/cheatcodes/contracts/roll_warp_tester.cairo").contract_address
        contract_address = deploy_contract("tests/integration/pure_cairo_vm/cheatcodes/send_message_to_l2/external_contract_with_l1_handler.cairo").contract_address
        fake_block_timestamp = 321
        warp(tester_address, fake_block_timestamp)
        send_message_to_l2(
            function_name="call_set_block_timestamp",
            from_address=123,
            to_address=contract_address,
            payload=[tester_address],
        )
        result = call(contract_address, "get_state")
        assert [fake_block_timestamp] == result, f"Expected '{[fake_block_timestamp]}', but got: '{result}'"
    %}

    return ();
}
