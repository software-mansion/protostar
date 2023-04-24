use array::ArrayTrait;
use result::ResultTrait;

#[test]
fn test_prepare_no_ctor() {
    let class_hash = declare('minimal_no_ctor').unwrap();

    drop(prepare(class_hash, ArrayTrait::new()).unwrap());
}

#[test]
fn test_prepare_no_args() {
    let class_hash = declare('minimal_no_args').unwrap();

    drop(prepare(class_hash, ArrayTrait::new()).unwrap());
}

#[test]
fn test_prepare_with_args() {
    let class_hash = declare('minimal_with_args').unwrap();

    let mut calldata = ArrayTrait::new();
    calldata.append('name');
    drop(prepare(class_hash, calldata).unwrap());
}

#[test]
fn test_prepare_cairo0() {
    let class_hash = declare_cairo0('cairo0').unwrap();

    drop(prepare(class_hash, ArrayTrait::new()).unwrap());

}

#[test]
fn test_prepare_cairo0_w_ctor() {
    let class_hash = declare_cairo0('cairo0_w_ctor').unwrap();

    let mut calldata = ArrayTrait::new();
    calldata.append(200);
    drop(prepare(class_hash, calldata).unwrap());

}

#[test]
fn test_prepare_cairo0_w_ctor_no_args() {
    let class_hash = declare_cairo0('cairo0_w_ctor_no_args').unwrap();

    drop(prepare(class_hash, ArrayTrait::new()).unwrap());
}

use serde::Serde;
use minimal_custom_structures::MinimalContract::CustomStruct;
use minimal_custom_structures::MinimalContract::CustomStructSerde;


#[test]
fn test_custom_structures_usage() {
    let class_hash = declare('minimal_custom_structures').unwrap();
    let mut args = ArrayTrait::new();
    let cs = CustomStruct { a: 1, b: 2 };
    CustomStructSerde::serialize(ref args, cs);

    drop(prepare(class_hash, args).unwrap());
}
