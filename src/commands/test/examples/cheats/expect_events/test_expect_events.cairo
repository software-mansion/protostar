%lang starknet

@event
func foobar(number : felt):
end

@event
func foobaz():
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

@view
func test_expect_event_by_name{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_events("foobar") %}
    emit_foobar(42)
    return ()
end

@view
func test_expect_event_by_name_and_data{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_events({"name": "foobar", "data": [42]}) %}
    emit_foobar(42)
    return ()
end

@view
func test_revert_on_data_mismatch{syscall_ptr : felt*, range_check_ptr}():
    %{
        expect_revert("EXPECTED_EVENT")
        expect_events({"name": "foobar", "data": [21]})
    %}
    emit_foobar(42)
    return ()
end

@view
func test_revert_when_no_events_were_emitted{syscall_ptr : felt*, range_check_ptr}():
    %{
        expect_revert("EXPECTED_EVENT")
        expect_events("foobar")
    %}
    return ()
end

@view
func test_expect_event_emitted_by_external_contract{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_events("balance_increased") %}
    alloc_locals
    local contract_address : felt
    %{ ids.contract_address = deploy_contract("./src/commands/test/examples/cheats/expect_events/basic_contract.cairo").contract_address %}
    BasicContract.increase_balance(contract_address=contract_address)
    return ()
end

@view
func test_expect_event_by_contract_address{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local contract_address : felt
    %{
        ids.contract_address = deploy_contract("./src/commands/test/examples/cheats/expect_events/basic_contract.cairo").contract_address
        expect_events({"name": "balance_increased", "from_address": ids.contract_address})
    %}
    BasicContract.increase_balance(contract_address=contract_address)
    return ()
end

@view
func test_revert_on_contract_address_mismatch{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local contract_address : felt
    %{
        ids.contract_address = deploy_contract("./src/commands/test/examples/cheats/expect_events/basic_contract.cairo").contract_address
        expect_revert("EXPECTED_EVENT", '{"name": "balance_increased", "from_address": "123"}')
        expect_events({"name": "balance_increased", "from_address": 123})
    %}
    BasicContract.increase_balance(contract_address=contract_address)
    return ()
end

@view
func test_expect_events_in_declared_order{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_events({"name": "foobar", "data": [21]}, {"name": "foobar", "data": [37]}) %}
    emit_foobar(21)
    emit_foobar(37)
    return ()
end

@view
func test_message_about_first_not_found_event{syscall_ptr : felt*, range_check_ptr}():
    %{
        expect_revert("EXPECTED_EVENT", '[21]')
        expect_events({"name": "foobar", "data": [37]}, {"name": "foobar", "data": [21]})
    %}
    emit_foobar(21)
    emit_foobar(37)
    return ()
end

@view
func test_allow_checking_for_events_in_any_order{syscall_ptr : felt*, range_check_ptr}():
    %{
        expect_events("foobar")
        expect_events("foobaz")
    %}
    foobaz.emit()
    emit_foobar(42)
    return ()
end
