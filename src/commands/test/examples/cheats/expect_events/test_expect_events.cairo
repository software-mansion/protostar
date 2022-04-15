%lang starknet

@event
func foobar(number : felt):
end

func emit_foobar{syscall_ptr : felt*, range_check_ptr}(number : felt):
    foobar.emit(number)
    return ()
end

@contract_interface
namespace BasicContract:
    func increase_balance():
    end
end
# ----------------------------------------------------------

# @view
# func test_expecting_event_by_name{syscall_ptr : felt*, range_check_ptr}():
#     %{ expect_events("foobar") %}
#     emit_foobar(42)
#     return ()
# end

# @view
# func test_stop_expecting_event{syscall_ptr : felt*, range_check_ptr}():
#     %{ expect_events("foobar") %}
#     emit_foobar(42)
#     return ()
# end

# @view
# func test_expecting_event_by_name_and_data{syscall_ptr : felt*, range_check_ptr}():
#     %{ expect_events({"name": "foobar", "data": [42]}) %}
#     emit_foobar(42)
#     return ()
# end

# @view
# func test_failing_when_event_was_not_emitted{syscall_ptr : felt*, range_check_ptr}():
#     %{
#         expect_revert("EXPECTED_EMIT")
#         expect_events("foobar")
#     %}
#     return ()
# end

# @view
# func test_event_emitted_by_external_contract{syscall_ptr : felt*, range_check_ptr}():
#     %{ expect_events("balance_increased") %}
#     alloc_locals
#     local contract_address : felt
#     %{ ids.contract_address = deploy_contract("./src/commands/test/examples/cheats/expect_events/basic_contract.cairo").contract_address %}
#     BasicContract.increase_balance(contract_address=contract_address)
#     return ()
# end

# @view
# func test_event_contract_address{syscall_ptr : felt*, range_check_ptr}():
#     alloc_locals
#     local contract_address : felt
#     %{
#         ids.contract_address = deploy_contract("./src/commands/test/examples/cheats/expect_events/basic_contract.cairo").contract_address
#         expect_events({"name": "balance_increased", "from_address": ids.contract_address})
#     %}
#     BasicContract.increase_balance(contract_address=contract_address)
#     return ()
# end

# @view
# func test_event_contract_address_mismatch{syscall_ptr : felt*, range_check_ptr}():
#     alloc_locals
#     local contract_address : felt
#     %{
#         ids.contract_address = deploy_contract("./src/commands/test/examples/cheats/expect_events/basic_contract.cairo").contract_address
#         expect_revert("EXPECTED_EMIT", '{"name": "balance_increased", "from_address": "123"}')
#         expect_events({"name": "balance_increased", "from_address": 123})
#     %}
#     BasicContract.increase_balance(contract_address=contract_address)
#     return ()
# end

# @view
# func test_emitted_events_order{syscall_ptr : felt*, range_check_ptr}():
#     %{ expect_events({"name": "foobar", "data": [21]}, {"name": "foobar", "data": [37]}) %}
#     emit_foobar(21)
#     emit_foobar(37)
#     return ()
# end

@view
func test_different_expected_events_order{syscall_ptr : felt*, range_check_ptr}():
    %{
        expect_revert("EXPECTED_EMIT", '[21]')
        expect_events({"name": "foobar", "data": [37]}, {"name": "foobar", "data": [21]})
    %}
    emit_foobar(21)
    emit_foobar(37)
    return ()
end

# test_expecting_event_twice
# test_failing_when_event_was_not_emitted
# test_failing_when_emitted_event_has_different_name
# test_failing_when_emitted_event_has_different_args
# test_event_emitted_before_calling_expect_emit
# test_showing_which_event_was_not_emitted
