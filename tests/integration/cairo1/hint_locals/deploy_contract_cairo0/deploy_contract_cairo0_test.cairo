use array::ArrayTrait;
use result::ResultTrait;


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
    match deploy_contract_cairo0('cairo0_w_ctor_error', args) {
       Result::Ok(contract_address) => assert(false, 'should not have deployed'),
       Result::Err(x) => assert(x == 101049956980219006924938593753655772187207156597769240626127871035476946994, x)
    }
}

