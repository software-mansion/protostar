%lang starknet

func roll(blk_number : felt):
    %{ syscall_handler.set_block_number(ids.blk_number) %}
    return ()
end

func warp(blk_timestamp : felt):
    %{ syscall_handler.set_block_timestamp(ids.blk_timestamp) %}
    return ()
end

func start_prank(caller_address : felt):
    %{ syscall_handler.set_caller_address(ids.caller_address) %}
    return ()
end

func stop_prank():
    %{ syscall_handler.set_caller_address(None) %}
    return ()
end

func mock_call(contract_address : felt):
    %{
        if mocked_fn_name is None:
            raise Exception("`mocked_fn_name` not found. Did you define `mocked_fn_name` inside a hint before calling this function?")

        from starkware.starknet.public.abi import get_selector_from_name

        selector = get_selector_from_name(mocked_fn_name)
        syscall_handler.register_mock_call(ids.contract_address, selector=selector, ret_data=mocked_ret_data)
    %}
    return ()
end

func clear_mock_call(contract_address : felt):
    %{
        if mocked_fn_name is None:
                raise Exception("`mocked_fn_name` not found. Did you define `mocked_fn_name` inside a hint before calling this function?")
        selector = get_selector_from_name(mocked_fn_name)
        syscall_handler.unregister_mock_call(ids.contract_address, selector)
    %}
    return ()
end

func except_revert():
    %{ __test_runner.except_revert() %}
    return ()
end
