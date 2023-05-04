use array::ArrayTrait;
use result::ResultTrait;
use core::cheatcodes::RevertedTransactionTrait;

#[test]
fn test_deploy() {
    let class_hash = declare('minimal').unwrap();
    assert(class_hash != 0, 'class_hash != 0');

    let prepare_result = prepare(class_hash, @ArrayTrait::new()).unwrap();

    assert(prepare_result.contract_address != 0, 'prepared contract_address != 0');
    assert(prepare_result.class_hash != 0, 'prepared class_hash != 0');

    let deployed_contract_address = deploy(prepare_result).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');
}

#[test]
fn test_deploy_cairo0() {
    let class_hash = declare_cairo0('cairo0').unwrap();
    assert(class_hash != 0, 'class_hash != 0');

    let prepare_result = prepare(class_hash, @ArrayTrait::new()).unwrap();

    assert(prepare_result.contract_address != 0, 'prepared contract_address != 0');
    assert(prepare_result.class_hash != 0, 'prepared class_hash != 0');

    let deployed_contract_address = deploy(prepare_result).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');
}

#[test]
fn test_deploy_with_ctor() {
    let mut constructor_calldata = ArrayTrait::new();
    constructor_calldata.append(1);
    constructor_calldata.append(2);

    let class_hash = declare('with_ctor').unwrap();
    assert(class_hash != 0, 'declared class_hash != 0');

    let prepare_result = prepare(class_hash, @constructor_calldata).unwrap();

    assert(prepare_result.contract_address != 0, 'prepared contract_address != 0');
    assert(prepare_result.class_hash != 0, 'prepared class_hash != 0');
    assert(prepare_result.constructor_calldata.len() == 2_u32, 'constructor_calldata size == 2');

    let deployed_contract_address = deploy(prepare_result).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');
}

#[test]
fn test_deploy_with_storage() {
    let class_hash = declare('with_storage').unwrap();
    assert(class_hash != 0, 'declared class_hash != 0');

    let prepare_result = prepare(class_hash, @ArrayTrait::new()).unwrap();

    assert(prepare_result.contract_address != 0, 'prepared contract_address != 0');
    assert(prepare_result.class_hash != 0, 'prepared class_hash != 0');
    assert(prepare_result.constructor_calldata.len() == 0_u32, 'constructor_calldata size == 0');

    let deployed_contract_address = deploy(prepare_result).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');
}

#[test]
fn test_deploy_with_ctor_invalid_calldata() {
    let mut constructor_calldata = ArrayTrait::new();
    constructor_calldata.append(1);

    let class_hash = declare('with_ctor').unwrap();
    assert(class_hash != 0, 'declared class_hash != 0');

    let prepare_result = prepare(class_hash, @constructor_calldata).unwrap();

    deploy(prepare_result).unwrap();
}

#[test]
fn test_deploy_with_ctor_panic() {
    let mut constructor_calldata = ArrayTrait::new();
    constructor_calldata.append(1);
    constructor_calldata.append(2);

    let class_hash = declare('with_ctor_panic').unwrap();
    assert(class_hash != 0, 'declared class_hash != 0');

    let prepare_result = prepare(class_hash, @constructor_calldata).unwrap();

    match deploy(prepare_result) {
        Result::Ok(_) => assert(false, 'no error was raised'),
        Result::Err(x) => assert(x.first() == 'panic', x.first()),
    }
}

#[test]
fn test_deploy_with_ctor_obsolete_calldata() {
    let mut constructor_calldata = ArrayTrait::new();
    constructor_calldata.append(1);
    constructor_calldata.append(2);

    let class_hash = declare('minimal').unwrap();
    assert(class_hash != 0, 'declared class_hash != 0');

    let prepare_result = prepare(class_hash, @constructor_calldata).unwrap();

    match deploy(prepare_result) {
        Result::Ok(_) => assert(false, 'no error was raised'),
        Result::Err(x) => assert(x.first() == 'No constructor was found', x.first()),
    }
}
