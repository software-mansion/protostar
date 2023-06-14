use array::ArrayTrait;
use protostar_print::PrintTrait;
use result::ResultTrait;

#[test]
fn test_print_basic() {
  1.print();

  'hello'.print();

  let mut array = ArrayTrait::new();
  array.append('veni');
  array.append('vidi');
  array.append('vici');
  array.print();

  (1 == 2).print();

  true.print();
  128.print();
  3618502788666131213697322783095070105623107215331596699973092056135872020480.print(); // felt252 max val

  assert(1 == 1, 'xxx');
}
