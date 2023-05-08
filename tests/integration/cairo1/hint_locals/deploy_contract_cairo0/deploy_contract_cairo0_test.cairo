use array::ArrayTrait;
use result::ResultTrait;
use cheatcodes::RevertedTransactionTrait;

#[test]
fn test_deploy_contract_cairo0() {
    let contract_address = deploy_contract_cairo0('cairo0', ArrayTrait::new()).unwrap();
    assert(contract_address != 0, 'contract_address != 0');
}

#[test]
fn test_deploy_contract_cairo0_w_ctor() {
    let mut args = ArrayTrait::new();
    args.append(100);
    let contract_address = deploy_contract_cairo0('cairo0_w_ctor', args).unwrap();
    assert(contract_address != 0, 'contract_address != 0');
}

#[test]
fn test_deploy_contract_cairo0_w_ctor_error() {
    let mut args = ArrayTrait::new();
    args.append(100);
    deploy_contract_cairo0('cairo0_w_ctor_error', args).unwrap();
}

