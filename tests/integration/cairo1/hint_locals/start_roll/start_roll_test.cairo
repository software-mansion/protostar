use array::ArrayTrait;
use result::ResultTrait;


#[test]
fn test_start_roll() {
    let deployed_contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let result = call(deployed_contract_address, 'check_block_number', @ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == -1, *result.at(0_u32));

    start_roll(100, deployed_contract_address);
    let result = call(deployed_contract_address, 'check_block_number', @ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == 100, *result.at(0_u32));
}

#[test]
fn test_start_roll_behind_a_proxy() {
    let target = deploy_contract('simple', @ArrayTrait::new()).unwrap();
    assert(target != 0, 'target != 0');

    let proxy = deploy_contract('proxy', @ArrayTrait::new()).unwrap();
    assert(proxy != 0, 'proxy != 0');

    start_roll(100, target);

    let mut calldata = ArrayTrait::new();
    calldata.append(target);

    let result = call(proxy, 'check_remote_block_number', @calldata).unwrap();
    assert(*result.at(0_u32) == 100, *result.at(0_u32));
}

#[test]
fn test_start_roll_with_invoke() {
    let deployed_contract_address = deploy_contract('storing_block_number', @ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let result = call(deployed_contract_address, 'retrieve_stored', @ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == 0, *result.at(0_u32));
    start_roll(100, deployed_contract_address);

    let result = invoke(deployed_contract_address, 'store_block_number', @ArrayTrait::new()).unwrap();

    let result = call(deployed_contract_address, 'retrieve_stored', @ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == 100, *result.at(0_u32));
}

#[test]
fn test_start_roll_constructor() {
    let class_hash = declare('storing_constructor_blk_number').unwrap();
    let prepared = prepare(class_hash, @ArrayTrait::new()).unwrap();

    start_roll(100, prepared.contract_address);

    let deployed_contract_address = deploy(prepared).unwrap();
    let result = call(deployed_contract_address, 'retrieve_stored', @ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == 100, *result.at(0_u32));
}

#[test]
fn test_start_stop_roll() {
    let deployed_contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let result = call(deployed_contract_address, 'check_block_number', @ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == -1, *result.at(0_u32));

    start_roll(100, deployed_contract_address);
    let result = call(deployed_contract_address, 'check_block_number', @ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == 100, *result.at(0_u32));

    stop_roll(deployed_contract_address);
    let result = call(deployed_contract_address, 'check_block_number', @ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == -1, *result.at(0_u32));
}

#[test]
fn test_start_roll_last_value_is_used() {
    let deployed_contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let result = call(deployed_contract_address, 'check_block_number', @ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == -1, *result.at(0_u32));

    start_roll(100, deployed_contract_address);
    start_roll(123, deployed_contract_address);

    let result = call(deployed_contract_address, 'check_block_number', @ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == 123, *result.at(0_u32));

    stop_roll(deployed_contract_address);
    let result = call(deployed_contract_address, 'check_block_number', @ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == -1, *result.at(0_u32));
}

#[test]
fn test_stop_roll_on_non_existent() {
    stop_roll(1234).unwrap();
}

#[test]
fn test_stop_roll_on_not_rolled() {
    let deployed_contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();

    stop_roll(1234).unwrap();
}

#[test]
fn test_stop_roll_multiple_times() {
    let deployed_contract_address = deploy_contract('simple', @ArrayTrait::new()).unwrap();
    start_roll(123, deployed_contract_address).unwrap();

    stop_roll(deployed_contract_address).unwrap();
    stop_roll(deployed_contract_address).unwrap();
}
