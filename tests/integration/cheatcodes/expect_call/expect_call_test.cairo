%lang starknet

@contract_interface
namespace MainContract {
  func get_id() -> (res: felt) {
  }
  func increase_balance(amount_1: felt, amount_2: felt, amount_3: felt) -> () {
  }
  func get_balance() -> (res: felt) {
  }
}

@external
func __setup__() {
  %{ context.ctr_addr_a = deploy_contract("./basic_contract.cairo", [123, 100]).contract_address %}
  %{
    declared = declare("./basic_contract.cairo")
    prepared = prepare(declared, [124, 120])
    context.ctr_addr_b = deploy(prepared).contract_address
  %}

  return ();
}

@external
func test_expect_call_success{syscall_ptr: felt*, range_check_ptr}() {
  tempvar ctr_addr_a;
  %{ ids.ctr_addr_a = context.ctr_addr_a %}
  tempvar ctr_addr_b;
  %{ ids.ctr_addr_b = context.ctr_addr_b %}
  %{
    expect_call(ids.ctr_addr_a, [5, 6, 7])
    expect_call(ids.ctr_addr_b, [1, 2, 3])
  %}

  MainContract.increase_balance(contract_address=ctr_addr_a, amount_1=5, amount_2=6, amount_3=7);
  MainContract.increase_balance(contract_address=ctr_addr_b, amount_1=1, amount_2=2, amount_3=3);

  return ();
}

@external
func test_expect_call_partial_success{syscall_ptr: felt*, range_check_ptr}() {
  tempvar ctr_addr_a;
  %{ ids.ctr_addr_a = context.ctr_addr_a %}
  tempvar ctr_addr_b;
  %{ ids.ctr_addr_b = context.ctr_addr_b %}
  %{
    expect_call(ids.ctr_addr_a, [7, 5, 6])
    expect_call(ids.ctr_addr_b, [0, 1, 2, 3, 4, 5, 6, 7])
  %}

  MainContract.increase_balance(contract_address=ctr_addr_a, amount_1=5, amount_2=6, amount_3=7);
  MainContract.increase_balance(contract_address=ctr_addr_b, amount_1=1, amount_2=3, amount_3=6);

  return ();
}

@external
func test_expect_call_wrong_address{syscall_ptr: felt*, range_check_ptr}() {
  tempvar ctr_addr_a;
  %{ ids.ctr_addr_a = context.ctr_addr_a %}
  tempvar ctr_addr_b;
  %{ ids.ctr_addr_b = context.ctr_addr_b %}
  %{
    expect_call(ids.ctr_addr_b, [1, 2, 3])
  %}

  MainContract.increase_balance(contract_address=ctr_addr_a, amount_1=1, amount_2=2, amount_3=3);

  return ();
}

@external
func test_expect_call_wrong_calldata{syscall_ptr: felt*, range_check_ptr}() {
  tempvar ctr_addr_a;
  %{ ids.ctr_addr_a = context.ctr_addr_a %}
  tempvar ctr_addr_b;
  %{ ids.ctr_addr_b = context.ctr_addr_b %}
  %{
    expect_call(ids.ctr_addr_a, [1, 2, 4])
  %}

  MainContract.increase_balance(contract_address=ctr_addr_a, amount_1=1, amount_2=2, amount_3=3);

  return ();
}