%lang starknet
from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.hash import hash2

@contract_interface
namespace BasicContract {
    func increase_balance(amount: felt) {
    }

    func get_balance() -> (res: felt) {
    }
}

func helper{pedersen_ptr: HashBuiltin*}() -> (a: felt, b: felt) {
    // [ap + 2000] = 111;
    // [ap + 10000] = 222;
    let (z) = hash2{hash_ptr=pedersen_ptr}(1, 2);
    assert z = z;
    return (1, 2);
}

func helper3{pedersen_ptr: HashBuiltin*}() -> (a: felt, b: felt) {
    // [ap + 2000] = 111;
    // [ap + 10000] = 222;
    let (k) = hash2{hash_ptr=pedersen_ptr}(1, 2);
    assert k = k;
    return (1,2);
}



func helper2{pedersen_ptr: HashBuiltin*}() -> (a: felt, b: felt) {
    // [ap + 2000] = 111;
    // [ap + 10000] = 222;
    let (c,d) = helper3();
    assert c = c;
    let (k) = hash2{hash_ptr=pedersen_ptr}(1, 2);
    assert k = k;
    return (1,2);
}

@external
func test_deploy_contract_simplified{syscall_ptr: felt*, range_check_ptr, pedersen_ptr: HashBuiltin*}() {
    alloc_locals;
    local contract_address: felt;
    let (z) = hash2{hash_ptr=pedersen_ptr}(1, 2);
    assert z = z;
    %{
        basic_contract = deploy_contract("./tests/integration/profile_tests/basic_contract.cairo")
        ids.contract_address = basic_contract.contract_address
    %}
    let (a,b) = helper();
    let (c,d) = helper2();
    assert a = a;
    assert c = c;
    BasicContract.increase_balance(contract_address, 5);
    let (res) = BasicContract.get_balance(contract_address);
    assert res = 5;
    return ();
}

// @external
// func test_printing_resource_usage_in_integration_testing_approach{
//     syscall_ptr : felt*, range_check_ptr
// }():
//     alloc_locals

// local z: felt
//     %{
//         basic_contract = deploy_contract("tests/integration/profile_tests/basic_contract.cairo")
//         ids.z = basic_contract.contract_address
//     %}
//     # helper()
//     # helper2()
//     BasicContract.increase_balance(z, 5)
//     return ()
// end
