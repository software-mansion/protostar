%lang starknet

@event
func increase_balance_called(current_balance : felt, amount : felt):
end

func increase_balance{syscall_ptr : felt*, range_check_ptr}():
    increase_balance_called.emit(current_balance=37, amount=21)
    return ()
end

@view
func test_event_emitted_from_tested_contract{syscall_ptr : felt*, range_check_ptr}():
    %{ stop_expecting_emit = expect_emit("increase_balance_called", [37,21]) %}
    increase_balance()
    # %{ stop_expecting_emit() %}
    return ()
end

# test_event_emitted_by_external_contract
# test_failing_when_event_was_not_emitted
# test_failing_when_emitted_event_has_different_name
# test_failing_when_emitted_event_has_different_args
