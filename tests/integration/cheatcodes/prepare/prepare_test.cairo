%lang starknet

@external
func test_passing_constructor_data_as_list{syscall_ptr: felt*, range_check_ptr}() {
    %{
        declaration = declare("./tests/integration/cheatcodes/deploy_contract/basic_with_constructor_uint256.cairo")
        contract_address = prepare(declaration, [42, 0]).contract_address
        assert contract_address is not None
    %}

    return ();
}

@external
func test_data_transformation{syscall_ptr: felt*, range_check_ptr}() {
    %{
        declaration = declare("./tests/integration/cheatcodes/deploy_contract/basic_with_constructor_uint256.cairo")
        contract_address = prepare(declaration, { "initial_balance": 42 }).contract_address
        assert contract_address is not None
    %}

    return ();
}

@external
func test_address_can_be_created_deterministically{syscall_ptr: felt*, range_check_ptr}() {
    %{
        declaration = declare("./tests/integration/cheatcodes/deploy_contract/basic_with_constructor_uint256.cairo")
        contract_address = prepare(declaration, { "initial_balance": 42 }, salt=1).contract_address
        assert contract_address == 2823411742808915120454901118615706369754373144490595577290817165627901995128
    %}

    return ();
}
