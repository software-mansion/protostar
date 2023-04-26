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

  assert(1 == 1, 'xxx');
}

#[test]
fn test_print_in_contract() {
    let contract_address = deploy_contract('print_contract', ArrayTrait::new()).unwrap();
    assert(contract_address != 0, 'contract_address != 0');

    let mut calldata = ArrayTrait::new();
    calldata.append(3);
    calldata.append(24);
    calldata.append(72);

    call(contract_address, 'perform_print', calldata).unwrap();
}
