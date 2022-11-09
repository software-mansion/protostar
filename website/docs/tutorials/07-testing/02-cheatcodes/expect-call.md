# `expect_call`
```python
def expect_call(self, contract_address: int, fn_name: str, calldata: list[int]) -> None: ...
```
Allows to specify what calls to contracts' functions are expected in the code. You can use this cheatcode in any place in the code as it checks for the desired calls' existence at the very end of the program's execution.

`calldata` is a list of arguments that are expected for a certain call. The checking mechanism goes for a strict match, which means that the order, as well as the values of each element, have to be exactly the same.


```cairo title="Example"
%lang starknet

@contract_interface
namespace MainContract {
  func increase_balance(amount_1: felt, amount_2: felt, amount_3: felt) -> () {
  }
}

@external
func __setup__() {
  %{
    context.ctr_addr_a = deploy_contract("basic_contract.cairo", []).contract_address
    context.ctr_addr_b = deploy_contract("basic_contract.cairo", []).contract_address
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
    expect_call(ids.ctr_addr_a, "increase_balance", [5, 6, 7])
    expect_call(ids.ctr_addr_b, "increase_balance", [1, 2, 3])
  %}

  MainContract.increase_balance(contract_address=ctr_addr_a, amount_1=5, amount_2=6, amount_3=7);
  MainContract.increase_balance(contract_address=ctr_addr_b, amount_1=1, amount_2=2, amount_3=3);

  return ();
}

@external
func test_expect_call_wrong_args{syscall_ptr: felt*, range_check_ptr}() {
  tempvar ctr_addr_a;
  %{
    ids.ctr_addr_a = context.ctr_addr_a
    expect_call(ids.ctr_addr_a, "increase_balance", [1, 3, 2])
  %}

  MainContract.increase_balance(contract_address=ctr_addr_a, amount_1=1, amount_2=2, amount_3=3);

  return ();
}
```


`test_expect_call_wrong_args` will fail because even though the set of expected arguments is the same as the arguments in the call, the order is different so they **do not** strictly match.
