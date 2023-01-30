func test_happy_path() {
    %{
        msg_from_l1 = 530437
        contract_address = deploy_contract("l1_handler_contract").ok.contract_address
        assert send_message_to_l2(
            function_name="existing_handler",
            from_address=123,
            payload=[msg_from_l1],
            to_address=contract_address,
        ).err_code == 0 
        result = call(contract_address, "get_state").ok
        assert [msg_from_l1] == result, f"Expected '{[msg_from_l1]}', but got: '{result}'"
    %}
    return ();
}

func test_data_transformer() {
    %{
        msg_from_l1 = 530437
        contract_address = deploy_contract("l1_handler_contract").ok.contract_address
        assert send_message_to_l2(
            function_name="existing_handler",
            from_address=123,
            payload={"value": msg_from_l1},
            to_address=contract_address,
        ).err_code == 0
        result = call(contract_address, "get_state").ok
        assert [msg_from_l1] == result, f"Expected '{[msg_from_l1]}', but got: '{result}'"
    %}
    return ();
}

func test_other_cheatcodes_impact_l1_handler() {
    %{
        contract_address = deploy_contract("l1_handler_contract").ok.contract_address
        fake_block_timestamp = 321
        assert warp(contract_address, fake_block_timestamp).err_code == 0
        assert send_message_to_l2(
            function_name="on_l1_msg_set_block_timestamp",
            from_address=123,
            to_address=contract_address,
        ).err_code == 0
        result = call(contract_address, "get_state").ok
        assert [fake_block_timestamp] == result, f"Expected '{[fake_block_timestamp]}', but got: '{result}'"
    %}

    return ();
}

func test_other_cheatcodes_impact_contracts_called_from_l1_handler() {
    %{
        tester_address = deploy_contract("roll_warp_tester").ok.contract_address
        contract_address = deploy_contract("l1_handler_contract").ok.contract_address
        fake_block_timestamp = 321
        assert warp(tester_address, fake_block_timestamp).err_code == 0
        assert send_message_to_l2(
            function_name="call_set_block_timestamp",
            from_address=123,
            to_address=contract_address,
            payload=[tester_address],
        ).err_code == 0
        result = call(contract_address, "get_state").ok
        assert [fake_block_timestamp] == result, f"Expected '{[fake_block_timestamp]}', but got: '{result}'"
    %}

    return ();
}
