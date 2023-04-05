use array::ArrayTrait;
use result::ResultTrait;

// #[test]
// fn test_fib() {
//     let x = fib(0, 1, 13);
//     assert(x == 233, 'fib(0, 1, 13) == 233');
// }

#[test]
fn test_increase_balance() {
    let contract_address = deploy_contract('main', ArrayTrait::new()).unwrap();

    let result_before = call(contract_address, 'get_balance', ArrayTrait::new()).unwrap();
    assert(*result_before.at(0_u32) == 0, 'Invalid balance');

    let mut invoke_calldata = ArrayTrait::new();
    invoke_calldata.append(42);
    invoke(contract_address, 'increase_balance', invoke_calldata).unwrap();

    let result_after = call(contract_address, 'get_balance', ArrayTrait::new()).unwrap();
    assert(*result_after.at(0_u32) == 42, 'Invalid balance');
}

#[test]
fn test_cannot_increase_balance_with_negative_value() {
    let contract_address = deploy_contract('main', ArrayTrait::new()).unwrap();

    let result_before = call(contract_address, 'get_balance', ArrayTrait::new()).unwrap();
    assert(*result_before.at(0_u32) == 0, 'Invalid balance');

    let mut invoke_calldata = ArrayTrait::new();
    invoke_calldata.append(-10000);
    let invoke_result = invoke(contract_address, 'increase_balance', invoke_calldata);

    assert(invoke_result.is_err(), 'Invoke should fail');
    let err = invoke_result.unwrap_err();
    assert(err == 'Invoke failed', 'Invalid err message');
}