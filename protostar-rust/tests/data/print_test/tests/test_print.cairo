use array::ArrayTrait;
use protostar_print::PrintTrait;

#[test]
fn test_print() {
    123.print();
    'aaa'.print();

    let mut arr = ArrayTrait::new();
    arr.append(152);
    arr.append(124);
    arr.append(149);
    arr.print();

    (1 == 5).print();
    assert(1 == 1, 'simple check');
}
