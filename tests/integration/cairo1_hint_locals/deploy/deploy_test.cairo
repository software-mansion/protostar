use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_deploy() {
    let class_hash = declare('minimal').unwrap();
    assert(class_hash != 0, 'class_hash != 0');

    let prepare_result = prepare(class_hash, ArrayTrait::new()).unwrap();

    assert(prepare_result.contract_address != 0, 'prepared contract_address != 0');
    assert(prepare_result.class_hash != 0, 'prepared class_hash != 0');

    let prepared_contract = PreparedContract {
        contract_address: prepare_result.contract_address,
        class_hash: prepare_result.class_hash,
        constructor_calldata: prepare_result.constructor_calldata
    };
    let deployed_contract_address = deploy(prepared_contract).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');
}

#[test]
fn test_deploy_with_ctor() {
    let mut constructor_calldata = ArrayTrait::new();
    constructor_calldata.append(1);
    constructor_calldata.append(2);


    let class_hash = declare('with_ctor').unwrap();
    assert(class_hash != 0, 'declared class_hash != 0');

    let prepare_result = prepare(class_hash, constructor_calldata).unwrap();

    assert(prepare_result.contract_address != 0, 'prepared contract_address != 0');
    assert(prepare_result.class_hash != 0, 'prepared class_hash != 0');
    // TODO: check the length of the array, this produces: error: Variable was previously moved
    // https://github.com/software-mansion/protostar/issues/1717
    // assert(prepare_result.constructor_calldata.len() == 2_u32, 'constructor_calldata size == 2');

    let prepared_contract = PreparedContract {
        contract_address: prepare_result.contract_address,
        class_hash: prepare_result.class_hash,
        constructor_calldata: prepare_result.constructor_calldata
    };
    let deployed_contract_address = deploy(prepared_contract).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');
}

#[test]
fn test_deploy_with_ctor_invalid_calldata() {
    let mut constructor_calldata = ArrayTrait::new();
    constructor_calldata.append(1);


    let class_hash = declare('with_ctor').unwrap();
    assert(class_hash != 0, 'declared class_hash != 0');

    let prepare_result = prepare(class_hash, constructor_calldata).unwrap();

    let prepared_contract = PreparedContract {
        contract_address: prepare_result.contract_address,
        class_hash: prepare_result.class_hash,
        constructor_calldata: prepare_result.constructor_calldata
    };
    deploy(prepared_contract).unwrap();
}

#[test]
fn test_deploy_with_ctor_panic() {
    let mut constructor_calldata = ArrayTrait::new();
    constructor_calldata.append(1);
    constructor_calldata.append(2);


    let class_hash = declare('with_ctor_panic').unwrap();
    assert(class_hash != 0, 'declared class_hash != 0');

    let prepare_result = prepare(class_hash, constructor_calldata).unwrap();

    let prepared_contract = PreparedContract {
        contract_address: prepare_result.contract_address,
        class_hash: prepare_result.class_hash,
        constructor_calldata: prepare_result.constructor_calldata
    };
    deploy(prepared_contract).unwrap();
}

#[test]
fn test_deploy_with_ctor_panic_check_err_code() {
    let mut constructor_calldata = ArrayTrait::new();
    constructor_calldata.append(1);
    constructor_calldata.append(2);


    let class_hash = declare('with_ctor_panic').unwrap();
    assert(class_hash != 0, 'declared class_hash != 0');

    let prepare_result = prepare(class_hash, constructor_calldata).unwrap();

    let prepared_contract = PreparedContract {
        contract_address: prepare_result.contract_address,
        class_hash: prepare_result.class_hash,
        constructor_calldata: prepare_result.constructor_calldata
    };
    match deploy(prepared_contract) {
        Result::Ok(_) => {
            assert(false, 'panic');
        },
        Result::Err(err) => {
            assert(err == 71040974298098041582785264739058207689790761971295899515275945048047502191, 'proper error thrown');
        },
    }
}
