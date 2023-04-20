use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_prepare_no_ctor() {
    let class_hash = declare('minimal_no_ctor').unwrap();

    prepare(class_hash, ArrayTrait::new()).unwrap();
}

#[test]
fn test_prepare_no_args() {
    let class_hash = declare('minimal_no_args').unwrap();

    prepare(class_hash, ArrayTrait::new()).unwrap();
}

#[test]
fn test_prepare_with_args() {
    let class_hash = declare('minimal_with_args').unwrap();

    let mut calldata = ArrayTrait::new();
    calldata.append('name');
    prepare(class_hash, calldata).unwrap();
}
