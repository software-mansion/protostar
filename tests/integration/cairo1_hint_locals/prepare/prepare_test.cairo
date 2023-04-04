use array::ArrayTrait;
use result::ResultTrait;
use src::minimal_with_args::MinimalContractWithConstructor::Man;


#[test]
fn test_prepare_no_args() {
    let class_hash = declare('minimal_no_args').unwrap();

    let calldata = ArrayTrait::new();
    let prepared_contract = prepare(class_hash, calldata).unwrap();
    drop(prepared_contract);
}

#[test]
fn test_prepare_with_args() {
    let class_hash = declare('minimal_with_args').unwrap();
    let man = Man { hunger: 3, strength: 4 };

    let mut calldata = ArrayTrait::new();
    calldata.append('name');
    let prepared_contract = prepare(class_hash, calldata).unwrap();
    drop(prepared_contract);
}
