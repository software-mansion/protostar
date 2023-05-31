use result::ResultTrait;
use array::ArrayTrait;
use protostar_print::PrintTrait;

#[test]
fn test_declare_simple() {
    let class_hash = declare('main').unwrap();
    assert(class_hash == 273, 'proper class hash');

    let mut data = ArrayTrait::new();
    data.append(101);
    data.append(102);
    data.append(105);
    deploy(PreparedContract { contract_address: 123, class_hash: 123, constructor_calldata: @data }).unwrap();

    assert(1 == 1, 'simple check');
}
