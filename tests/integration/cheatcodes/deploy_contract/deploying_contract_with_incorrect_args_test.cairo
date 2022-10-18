%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin

@external
func test_deploying_contract_with_incorrect_args{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(){
     // Should have one constructor arg
    %{ deploy_contract('./tests/integration/cheatcodes/deploy_contract/basic_with_constructor.cairo') %}
    return ();
}

@external
func test_deploying_contract_with_incorrect_arg_types{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(){
     // Should have one constructor arg
    %{ deploy_contract('./tests/integration/cheatcodes/deploy_contract/basic_with_constructor.cairo', constructor_args={"initial_balance": {"low": 1, "high": 0}}) %}
    return ();
}