use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_deploy_contract_simple() {
    let deployed_contract_address = deploy_contract('minimal', ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');
}

#[test]
fn test_deploy_non_existing_contract() {
    let deployed_contract_address = deploy_contract('xxx', ArrayTrait::new()).unwrap();
}

#[test]
fn test_deploy_contract_with_constructor() {
    let mut constructor_calldata = ArrayTrait::new();
    constructor_calldata.append(3);
    constructor_calldata.append(2);

    let deployed_contract_address = deploy_contract('with_constructor', constructor_calldata).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');
}

#[test]
fn test_deploy_contract_with_constructor_panic() {
    let mut constructor_calldata = ArrayTrait::new();
    constructor_calldata.append(3);
    constructor_calldata.append(2);

    let deployed_contract_address = deploy_contract('with_constructor_panic', constructor_calldata).unwrap();
}

#[test]
fn test_deploy_contract_cairo0() {
    let deployed_contract_address = deploy_contract_cairo0('cairo0', ArrayTrait::new()).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');
}

#[test]
fn test_deploy_contract_cairo0_with_constructor() {
    let mut constructor_calldata = ArrayTrait::new();
    constructor_calldata.append(3);

    let deployed_contract_address = deploy_contract_cairo0('cairo0_with_constructor', constructor_calldata).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');
}

#[test]
fn test_deploy_contract_cairo0_using_cairo1() {
    let deployed_contract_address = deploy_contract('cairo0', ArrayTrait::new()).unwrap();
}
