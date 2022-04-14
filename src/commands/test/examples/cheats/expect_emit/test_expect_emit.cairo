%lang starknet

@event
func increase_balance_called(current_balance : felt, amount : felt):
end

func increase_balance{syscall_ptr : felt*, range_check_ptr}():
    increase_balance_called.emit(current_balance=37, amount=21)
    return ()
end

@contract_interface
namespace BasicContract:
    func increase_balance():
    end
end
# ----------------------------------------------------------

@view
func test_event_emitted_from_tested_contract{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_emit("increase_balance_called") %}
    increase_balance()
    return ()
end

# @view
# func test_failing_when_event_was_not_emitted{syscall_ptr : felt*, range_check_ptr}():
#     %{
#         stop_expecting_emit = expect_emit("increase_balance_called", [37,21])
#         expect_revert("EXPECTED_EMIT", "event_name: increase_balance_called, event_data: [37, 21]")
#         stop_expecting_emit()
#     %}
#     increase_balance()
#     return ()
# end

# @view
# func test_event_emitted_by_external_contract{syscall_ptr : felt*, range_check_ptr}():
#     alloc_locals

# local contract_address : felt
#     %{ ids.contract_address = deploy_contract("./src/commands/test/examples/cheats/expect_emit/basic_contract.cairo").contract_address %}

# %{ expect_emit("balance_increased") %}
#     BasicContract.increase_balance(contract_address=contract_address)

# return ()
# end

# test_failing_when_event_was_not_emitted
# test_failing_when_emitted_event_has_different_name
# test_failing_when_emitted_event_has_different_args
# test_event_emitted_before_calling_expect_emit
