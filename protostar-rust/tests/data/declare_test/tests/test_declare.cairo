use result::ResultTrait;
use protostar_print::PrintTrait;

#[test]
fn test_declare_simple() {
    assert(1==1, 'asd');
    let class_hash = declare('declare_test').unwrap();
    //assert(class_hash == 273, 'proper class hash');
}
