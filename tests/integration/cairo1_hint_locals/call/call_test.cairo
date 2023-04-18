
use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_call_simple() {
    let class_hash = declare('simple').unwrap();
    assert(class_hash != 0, 'class_hash != 0');

    let prepare_result = prepare(class_hash, ArrayTrait::new()).unwrap();

    assert(prepare_result.contract_address != 0, 'deployed contract_address != 0');
    assert(prepare_result.class_hash != 0, 'deployed class_hash != 0');

    let prepared_contract = PreparedContract {
        contract_address: prepare_result.contract_address,
        class_hash: prepare_result.class_hash,
        constructor_calldata: prepare_result.constructor_calldata
    };
    let deployed_contract_address = deploy(prepared_contract).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let return_data = call(deployed_contract_address, 'empty', ArrayTrait::new()).unwrap();
    assert(return_data.is_empty(), 'call result is empty');

    let mut calldata = ArrayTrait::new();
    calldata.append(3);
    calldata.append(2);
    calldata.append(5);
    let return_data2 = call(deployed_contract_address, 'perform', calldata).unwrap();
    assert(*return_data2.at(0_u32) == 25, 'check call result');
}

#[test]
fn test_call_with_ctor() {
    let class_hash = declare('with_ctor').unwrap();
    assert(class_hash != 0, 'class_hash != 0');

    let mut constructor_calldata = ArrayTrait::new();
    constructor_calldata.append(3);
    constructor_calldata.append(2);
    let prepare_result = prepare(class_hash, constructor_calldata).unwrap();

    assert(prepare_result.contract_address != 0, 'deployed contract_address != 0');
    assert(prepare_result.class_hash != 0, 'deployed class_hash != 0');

    let prepared_contract = PreparedContract {
        contract_address: prepare_result.contract_address,
        class_hash: prepare_result.class_hash,
        constructor_calldata: prepare_result.constructor_calldata
    };
    let deployed_contract_address = deploy(prepared_contract).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let return_data = call(deployed_contract_address, 'getme123', ArrayTrait::new()).unwrap();
    assert(*return_data.at(0_u32) == 123, 'call result is 123');
}

#[test]
fn test_call_cairo0() {
    let class_hash = declare_cairo0('cairo0').unwrap();
    assert(class_hash != 0, 'class_hash != 0');

    let prepare_result = prepare(class_hash, ArrayTrait::new()).unwrap();

    assert(prepare_result.contract_address != 0, 'deployed contract_address != 0');
    assert(prepare_result.class_hash != 0, 'deployed class_hash != 0');

    let prepared_contract = PreparedContract {
        contract_address: prepare_result.contract_address,
        class_hash: prepare_result.class_hash,
        constructor_calldata: prepare_result.constructor_calldata
    };

    let deployed_contract_address = deploy(prepared_contract).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let mut calldata = ArrayTrait::new();
    calldata.append(3);

    let return_data = call(deployed_contract_address, 'increase_balance', calldata).unwrap();
    assert(return_data.is_empty(), 'call result is empty');

    let return_data = call(deployed_contract_address, 'get_balance', ArrayTrait::new()).unwrap();
    assert(return_data.len() == 1_u32, 'call result contains value');
}

#[test]
fn test_call_cairo0_non_existing_entrypoint() {
    let class_hash = declare_cairo0('cairo0').unwrap();
    assert(class_hash != 0, 'class_hash != 0');

    let prepare_result = prepare(class_hash, ArrayTrait::new()).unwrap();

    assert(prepare_result.contract_address != 0, 'deployed contract_address != 0');
    assert(prepare_result.class_hash != 0, 'deployed class_hash != 0');

    let prepared_contract = PreparedContract {
        contract_address: prepare_result.contract_address,
        class_hash: prepare_result.class_hash,
        constructor_calldata: prepare_result.constructor_calldata
    };

    let deployed_contract_address = deploy(prepared_contract).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let mut calldata = ArrayTrait::new();
    calldata.append(3);

    call(deployed_contract_address, 'xxx', calldata).unwrap();
}

#[test]
fn test_call_wrong_name() {
    let class_hash = declare('simple').unwrap();
    assert(class_hash != 0, 'class_hash != 0');

    let prepare_result = prepare(class_hash, ArrayTrait::new()).unwrap();

    assert(prepare_result.contract_address != 0, 'deployed contract_address != 0');
    assert(prepare_result.class_hash != 0, 'deployed class_hash != 0');

    let prepared_contract = PreparedContract {
        contract_address: prepare_result.contract_address,
        class_hash: prepare_result.class_hash,
        constructor_calldata: prepare_result.constructor_calldata
    };
    let deployed_contract_address = deploy(prepared_contract).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    call(deployed_contract_address, 'empty_no_exist', ArrayTrait::new()).unwrap();
}

#[test]
fn test_call_wrong_number_of_args() {
    let class_hash = declare('simple').unwrap();
    assert(class_hash != 0, 'class_hash != 0');

    let prepare_result = prepare(class_hash, ArrayTrait::new()).unwrap();

    assert(prepare_result.contract_address != 0, 'deployed contract_address != 0');
    assert(prepare_result.class_hash != 0, 'deployed class_hash != 0');

    let prepared_contract = PreparedContract {
        contract_address: prepare_result.contract_address,
        class_hash: prepare_result.class_hash,
        constructor_calldata: prepare_result.constructor_calldata
    };
    let deployed_contract_address = deploy(prepared_contract).unwrap();
    assert(deployed_contract_address != 0, 'deployed_contract_address != 0');

    let mut calldata = ArrayTrait::new();
    calldata.append(3);
    calldata.append(2);
    call(deployed_contract_address, 'perform', calldata).unwrap();
}

#[test]
fn test_call_exception_handling() {
    let deployed_contract_address = deploy_contract('panicking_contract', ArrayTrait::new()).unwrap();

    match call(deployed_contract_address, 'go_bonkers', ArrayTrait::new()) {
        Result::Ok(_) => assert(false, 'bonkers contract did not panic'),
        Result::Err(x) => assert(x == 'i am bonkers', x),
    }
}