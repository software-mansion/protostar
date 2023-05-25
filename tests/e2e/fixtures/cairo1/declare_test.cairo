use result::ResultTrait;
use protostar_print::PrintTrait;

#[test]
fn test_declare_simple() {
    let class_hash = declare('main').unwrap();
    assert(class_hash == 273, 'proper class hash');

    assert(1 == 1, 'simple check');
}