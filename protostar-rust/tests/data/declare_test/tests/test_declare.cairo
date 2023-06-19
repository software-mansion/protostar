use result::ResultTrait;
use protostar_print::PrintTrait;

#[test]
fn test_declare_simple() {
    let class_hash = declare('declare_test').unwrap();
    assert(class_hash == 273, 'proper class hash');
}

#[test]
fn multiple_contracts() {
    let class_hash = declare('declare_test').unwrap();
    assert(class_hash == 273, 'proper class hash');

    let class_hash2 = declare('contract1').unwrap();
    assert(class_hash == 273, 'proper class hash');
}
