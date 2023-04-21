use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_prank() {
    let deployed_contract_address = deploy_contract('pranked', ArrayTrait::new()).unwrap();

    let return_data = call(deployed_contract_address, 'get_a', ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 0, 'check call result');

    invoke(deployed_contract_address, 'maybe_set_three', ArrayTrait::new()).unwrap();
    let return_data = call(deployed_contract_address, 'get_a', ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 2, 'check call result');

    start_prank(123, deployed_contract_address).unwrap();

    invoke(deployed_contract_address, 'maybe_set_three', ArrayTrait::new()).unwrap();
    let return_data = call(deployed_contract_address, 'get_a', ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 3, 'check call result');

    stop_prank(deployed_contract_address).unwrap();

    invoke(deployed_contract_address, 'maybe_set_three', ArrayTrait::new()).unwrap();
    let return_data = call(deployed_contract_address, 'get_a', ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 2, 'check call result');
}

#[test]
fn test_stop_prank_on_non_existent() {
    stop_prank(1234).unwrap();
}

#[test]
fn test_stop_prank_on_not_pranked() {
    let deployed_contract_address = deploy_contract('pranked', ArrayTrait::new()).unwrap();

    stop_prank(1234).unwrap();

    invoke(deployed_contract_address, 'maybe_set_three', ArrayTrait::new()).unwrap();
    let return_data = call(deployed_contract_address, 'get_a', ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 2, 'check call result');
}

#[test]
fn test_stop_prank_multiple_times() {
    let deployed_contract_address = deploy_contract('pranked', ArrayTrait::new()).unwrap();
    start_prank(123, deployed_contract_address).unwrap();

    stop_prank(deployed_contract_address).unwrap();
    stop_prank(deployed_contract_address).unwrap();
}

#[test]
fn test_start_prank_latest_takes_precedence() {
    let deployed_contract_address = deploy_contract('pranked', ArrayTrait::new()).unwrap();

    start_prank(123, deployed_contract_address).unwrap();
    start_prank(111, deployed_contract_address).unwrap();

    invoke(deployed_contract_address, 'maybe_set_three', ArrayTrait::new()).unwrap();
    let return_data = call(deployed_contract_address, 'get_a', ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 2, 'check call result');

    start_prank(111, deployed_contract_address).unwrap();
    start_prank(123, deployed_contract_address).unwrap();

    invoke(deployed_contract_address, 'maybe_set_three', ArrayTrait::new()).unwrap();
    let return_data = call(deployed_contract_address, 'get_a', ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 3, 'check call result');
}

#[test]
fn test_stop_prank_cancels_all_pranks() {
    let deployed_contract_address = deploy_contract('pranked', ArrayTrait::new()).unwrap();

    start_prank(123, deployed_contract_address).unwrap();
    start_prank(123, deployed_contract_address).unwrap();

    invoke(deployed_contract_address, 'maybe_set_three', ArrayTrait::new()).unwrap();
    let return_data = call(deployed_contract_address, 'get_a', ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 3, 'check call result');

    stop_prank(deployed_contract_address).unwrap();

    invoke(deployed_contract_address, 'maybe_set_three', ArrayTrait::new()).unwrap();
    let return_data = call(deployed_contract_address, 'get_a', ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 2, 'check call result');
}