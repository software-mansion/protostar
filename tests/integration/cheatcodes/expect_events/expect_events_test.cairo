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

@external
func __setup__():
    %{ context.contract_address = deploy_contract("./tests/integration/cheatcodes/expect_events/basic_contract.cairo").contract_address %}
    return ()
end

# ----------------------------------------------------------

@external
func test_expect_event_by_name{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_events("foobar") %}
    emit_foobar(42)
    return ()
end

@external
func test_expect_event_by_name_and_data{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_events({"name": "foobar", "data": [42]}) %}
    emit_foobar(42)
    return ()
end

@external
func test_fail_on_data_mismatch{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_events({"name": "foobar", "data": [21]}) %}
    emit_foobar(42)
    return ()
end

@external
func test_fail_when_no_events_were_emitted{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_events("foobar") %}
    return ()
end

@external
func test_expect_event_emitted_by_external_contract{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_events("balance_increased") %}
    alloc_locals
    local contract_address : felt
    %{ ids.contract_address = deploy_contract("./tests/integration/cheatcodes/expect_events/basic_contract.cairo").contract_address %}
    BasicContract.increase_balance(contract_address=contract_address)
    return ()
end

@external
func test_expect_event_by_contract_address{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local contract_address : felt
    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/expect_events/basic_contract.cairo").contract_address
        expect_events({"name": "balance_increased", "from_address": ids.contract_address})
    %}
    BasicContract.increase_balance(contract_address=contract_address)
    return ()
end

@external
func test_fail_on_contract_address_mismatch{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local contract_address : felt
    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/expect_events/basic_contract.cairo").contract_address
        expect_events({"name": "balance_increased", "from_address": 123})
    %}
    BasicContract.increase_balance(contract_address=contract_address)
    return ()
end

@external
func test_expect_events_in_declared_order{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_events({"name": "foobar", "data": [21]}, {"name": "foobar", "data": [37]}) %}
    emit_foobar(21)
    emit_foobar(37)
    return ()
end

@external
func test_fail_message_about_first_not_found_event{syscall_ptr : felt*, range_check_ptr}():
    %{ expect_events({"name": "foobar", "data": [37]}, {"name": "foobar", "data": [21]}) %}
    emit_foobar(21)
    emit_foobar(37)
    return ()
end

@external
func test_allow_checking_for_events_in_any_order{syscall_ptr : felt*, range_check_ptr}():
    %{
        expect_events("foobar")
        expect_events("foobaz")
    %}
    foobaz.emit()
    emit_foobar(42)
    return ()
end

@external
func test_selector_to_name_mapping{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local contract_address : felt
    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/expect_events/basic_contract.cairo").contract_address
        expect_events("foobaz")
    %}
    emit_foobar(21)
    BasicContract.increase_balance(contract_address=contract_address)

    # assert in the pytest file
    return ()
end

@external
func test_data_transformation{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local contract_address : felt
    %{
        ids.contract_address = deploy_contract("./tests/integration/cheatcodes/expect_events/basic_contract.cairo").contract_address
        expect_events({"name": "balance_increased", "data": {"current_balance" : 37, "amount" : 21}})
    %}
    BasicContract.increase_balance(contract_address=contract_address)

    return ()
end

@external
func test_data_transformation_in_contract_deployed_in_setup{syscall_ptr : felt*, range_check_ptr}():
    alloc_locals
    local contract_address : felt
    %{
        ids.contract_address = context.contract_address
        expect_events({"name": "balance_increased", "data": {"current_balance" : 37, "amount" : 21}})
    %}
    BasicContract.increase_balance(contract_address=contract_address)

    return ()
end
