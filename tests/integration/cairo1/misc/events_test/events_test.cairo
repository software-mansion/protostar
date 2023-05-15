use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_events_simple() {
    let deployed_contract_address = deploy_contract('simple', ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    invoke(deployed_contract_address, 'generate_event', ArrayTrait::new()).unwrap();
}

#[test]
fn test_events_with_data() {
    let deployed_contract_address = deploy_contract('with_data', ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    invoke(deployed_contract_address, 'generate_event', ArrayTrait::new()).unwrap();
}
