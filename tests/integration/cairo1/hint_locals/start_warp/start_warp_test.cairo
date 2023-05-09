use array::ArrayTrait;
use result::ResultTrait;


#[test]
fn test_start_warp() {
    let deployed_contract_address = deploy_contract('simple', ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let result = call(deployed_contract_address, 'check_timestamp', ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == 0, *result.at(0_u32));

    start_warp(100, deployed_contract_address);
    let result = call(deployed_contract_address, 'check_timestamp', ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == 100, *result.at(0_u32));
}

#[test]
fn test_start_warp_behind_a_proxy() {
    let target = deploy_contract('simple', ArrayTrait::new()).unwrap();
    assert(target != 0, 'target != 0');

    let proxy = deploy_contract('proxy', ArrayTrait::new()).unwrap();
    assert(proxy != 0, 'proxy != 0');

    start_warp(100, target);

    let mut calldata = ArrayTrait::new();
    calldata.append(target);

    let result = call(proxy, 'check_remote_timestamp', calldata).unwrap();
    assert(*result.at(0_u32) == 100, *result.at(0_u32));
}

#[test]
fn test_start_warp_with_invoke() {
    let deployed_contract_address = deploy_contract('storing_timestamp', ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let result = call(deployed_contract_address, 'retrieve_stored', ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == 0, *result.at(0_u32));
    start_warp(100, deployed_contract_address);

    let result = invoke(deployed_contract_address, 'store_timestamp', ArrayTrait::new()).unwrap();

    let result = call(deployed_contract_address, 'retrieve_stored', ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == 100, *result.at(0_u32));
}

#[test]
fn test_start_warp_constructor() {
    let class_hash = declare('storing_constructor_timestamp').unwrap();
    let prepared = prepare(class_hash, ArrayTrait::new()).unwrap();

    start_warp(100, prepared.contract_address);

    let deployed_contract_address = deploy(prepared).unwrap();
    let result = call(deployed_contract_address, 'retrieve_stored', ArrayTrait::new()).unwrap();
    assert(*result.at(0_u32) == 100, *result.at(0_u32));
}