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
