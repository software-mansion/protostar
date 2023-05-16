use array::ArrayTrait;
use result::ResultTrait;
use cheatcodes::RevertedTransactionTrait;

#[test]
fn test_invoke_simple() {
    let deployed_contract_address = deploy_contract('get_set', @ArrayTrait::new()).unwrap();

    let return_data = call(deployed_contract_address, 'get_a', @ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 0, 'check call result');

    let mut calldata = ArrayTrait::new();
    calldata.append(3);

    invoke(deployed_contract_address, 'set_a', @calldata).unwrap();

    let return_data2 = call(deployed_contract_address, 'get_a', @ArrayTrait::new()).unwrap();
    assert(*return_data2.at(0_u32) == 3, 'check call result 2');
}

#[test]
fn test_invoke_cairo0() {
    let class_hash = declare_cairo0('cairo0').unwrap();
    let prepared = prepare(class_hash, @ArrayTrait::new()).unwrap();
    let deployed_contract_address = deploy(prepared).unwrap();

    let return_data = call(deployed_contract_address, 'get_balance', @ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 0, 'check call result');

    let mut calldata = ArrayTrait::new();
    calldata.append(10);

    invoke(deployed_contract_address, 'increase_balance', @calldata).unwrap();

    let return_data2 = call(deployed_contract_address, 'get_balance', @ArrayTrait::new()).unwrap();
    assert(*return_data2.at(0_u32) == 10, 'check call result 2');
}

#[test]
fn test_invoke_with_ctor() {
    let mut calldata = ArrayTrait::new();
    calldata.append(10);

    let deployed_contract_address = deploy_contract('get_set_with_ctor', @calldata).unwrap();

    let return_data = call(deployed_contract_address, 'get_a', @ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 10, 'check call result');

    let mut calldata = ArrayTrait::new();
    calldata.append(3);

    invoke(deployed_contract_address, 'set_a', @calldata).unwrap();

    let return_data2 = call(deployed_contract_address, 'get_a', @ArrayTrait::new()).unwrap();
    assert(*return_data2.at(0_u32) == 3, 'check call result 2');
}

#[test]
fn test_invoke_wrong_number_of_args() {
    let deployed_contract_address = deploy_contract('get_set', @ArrayTrait::new()).unwrap();
    let mut calldata = ArrayTrait::new();
    calldata.append(3);
    calldata.append(2);
    invoke(deployed_contract_address, 'set_a', @calldata).unwrap();
}

#[test]
fn test_invoke_non_existing_function() {
    let deployed_contract_address = deploy_contract('get_set', @ArrayTrait::new()).unwrap();
    invoke(deployed_contract_address, 'set_b', @ArrayTrait::new()).unwrap();
}

#[test]
fn test_invoke_cairo0_wrong_number_of_args() {
    let class_hash = declare_cairo0('cairo0').unwrap();
    let prepared = prepare(class_hash, @ArrayTrait::new()).unwrap();
    let deployed_contract_address = deploy(prepared).unwrap();

    let mut calldata = ArrayTrait::new();
    calldata.append(3);
    calldata.append(2);
    invoke(deployed_contract_address, 'increase_balance', @calldata).unwrap();
}

#[test]
fn test_invoke_cairo0_non_existing_function() {
    let class_hash = declare_cairo0('cairo0').unwrap();
    let prepared = prepare(class_hash, @ArrayTrait::new()).unwrap();
    let deployed_contract_address = deploy(prepared).unwrap();

    invoke(deployed_contract_address, 'set_balance', @ArrayTrait::new()).unwrap();
}

#[test]
fn test_invoke_vs_call_state_changes() {
    let deployed_contract_address = deploy_contract('get_set', @ArrayTrait::new()).unwrap();

    let return_data = call(deployed_contract_address, 'get_a', @ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 0, 'check call result 2'); // Unchanged

    let mut calldata = ArrayTrait::new();
    calldata.append(3);
    call(deployed_contract_address, 'set_a', @calldata).unwrap();

    let return_data = call(deployed_contract_address, 'get_a', @ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 0, 'check call result 2'); // Unchanged

    let mut calldata2 = ArrayTrait::new();
    calldata2.append(3);
    invoke(deployed_contract_address, 'set_a', @calldata2).unwrap();

    let return_data2 = call(deployed_contract_address, 'get_a', @ArrayTrait::new()).unwrap();
    assert(*return_data2.at(0_u32) == 3, 'check call result 2'); // Changed
}

#[test]
fn test_invoke_exception_handling() {
    let deployed_contract_address = deploy_contract('panicking_contract', @ArrayTrait::new()).unwrap();

    match invoke(deployed_contract_address, 'go_bonkers', @ArrayTrait::new()) {
        Result::Ok(_) => assert(false, 'contract did not panic'),
        Result::Err(x) => assert(x.first() == 'i am bonkers', x.first()),
    }
}

#[test]
fn test_invoke_doesnt_move_calldata() {
    let deployed_contract_address = deploy_contract('get_set', @ArrayTrait::new()).unwrap();

    let mut calldata = ArrayTrait::new();
    calldata.append(3);

    invoke(deployed_contract_address, 'set_a', @calldata).unwrap();

    // This should work if calldata is not moved to invoke
    assert(calldata.len() == 1_u32, 'calldata size == 1');
}
