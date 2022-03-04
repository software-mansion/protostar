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

func mock_call(contract_address : felt, selector : felt, ret_data : felt):
    %{ syscall_handler.register_mock_call(ids.contract_address, selector=ids.selector, ret_data=[ids.ret_data]) %}
    return ()
end
