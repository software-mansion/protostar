use array::ArrayTrait;
use result::ResultTrait;
use cheatcodes::RevertedTransactionTrait;

#[test]
fn test_call_simple() {
    let deployed_contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let return_data = call(deployed_contract_address, 'empty', @ArrayTrait::new()).unwrap();
    assert(return_data.is_empty(), 'call result is empty');

    let mut calldata = ArrayTrait::new();
    calldata.append(3);
    calldata.append(2);
    calldata.append(5);
    let return_data2 = call(deployed_contract_address, 'perform', @calldata).unwrap();
    assert(*return_data2.at(0_u32) == 25, 'check call result');
}

#[test]
fn test_call_not_mutating_state() {
    let mut constructor_calldata = ArrayTrait::new();
    constructor_calldata.append(100);
    let deployed_contract_address = deploy_contract('with_storage', @constructor_calldata).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let return_data = call(deployed_contract_address, 'get_a', @ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 100, 'call result is 100');

    let mut calldata = ArrayTrait::new();
    calldata.append(200);
    let return_data2 = call(deployed_contract_address, 'set_a', @calldata).unwrap();
    assert(return_data2.is_empty(), 'call result is empty');

    let return_data3 = call(deployed_contract_address, 'get_a', @ArrayTrait::new()).unwrap();
    assert(*return_data3.at(0_u32) == 100, 'call result is 100');
}

#[test]
fn test_call_cairo0() {
    let deployed_contract_address = deploy_contract_cairo0('cairo0', @ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let mut calldata = ArrayTrait::new();
    calldata.append(3);

    let return_data = call(deployed_contract_address, 'increase_balance', @calldata).unwrap();
    assert(return_data.is_empty(), 'call result is empty');

    let return_data = call(deployed_contract_address, 'get_balance', @ArrayTrait::new()).unwrap();
    assert(return_data.len() == 1_u32, 'call result contains value');
}

#[test]
fn test_call_cairo0_non_existing_entrypoint() {
    let deployed_contract_address = deploy_contract_cairo0('cairo0', @ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let mut calldata = ArrayTrait::new();
    calldata.append(3);

    call(deployed_contract_address, 'xxx', @calldata).unwrap();
}

#[test]
fn test_call_wrong_name() {
    let deployed_contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    call(deployed_contract_address, 'empty_no_exist', @ArrayTrait::new()).unwrap();
}

#[test]
fn test_call_wrong_number_of_args() {
    let deployed_contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let mut calldata = ArrayTrait::new();
    calldata.append(3);
    calldata.append(2);
    call(deployed_contract_address, 'perform', @calldata).unwrap();
}

#[test]
fn test_call_exception_handling() {
    let deployed_contract_address = deploy_contract('panicking_contract', @ArrayTrait::new()).unwrap();

    match call(deployed_contract_address, 'go_bonkers', @ArrayTrait::new()) {
        Result::Ok(_) => assert(false, 'bonkers contract did not panic'),
        Result::Err(x) => assert(x.first() == 'i am bonkers', x.first()),
    }
}

#[test]
fn test_call_doesnt_move_calldata() {
    let deployed_contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();

    let mut calldata = ArrayTrait::new();
    calldata.append(3);
    calldata.append(2);
    calldata.append(5);
    let return_data = call(deployed_contract_address, 'perform', @calldata).unwrap();

    // This should work if calldata is not moved to call
    assert(calldata.len() == 3_u32, 'calldata size == 3');
}
