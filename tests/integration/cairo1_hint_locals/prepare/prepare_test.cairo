use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_prepare_no_ctor() {
    let class_hash = declare('minimal_no_ctor').unwrap();

    let prepared_contract = prepare(class_hash, ArrayTrait::new()).unwrap();
    drop(prepared_contract);
}

#[test]
fn test_prepare_no_args() {
    let class_hash = declare('minimal_no_args').unwrap();

    let prepared_contract = prepare(class_hash, ArrayTrait::new()).unwrap();
    drop(prepared_contract);
}

#[test]
fn test_prepare_with_args() {
    let class_hash = declare('minimal_with_args').unwrap();

    let mut calldata = ArrayTrait::new();
    calldata.append('name');
    let prepared_contract = prepare(class_hash, calldata).unwrap();
    drop(prepared_contract);
}
