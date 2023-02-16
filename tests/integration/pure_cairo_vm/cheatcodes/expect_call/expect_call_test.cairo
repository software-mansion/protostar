func test_expect_call_success() {
  %{
    addr = deploy_contract("./src/basic.cairo").ok.contract_address
    expect_call(addr, "get_balance", [])
    call(addr, "get_balance").ok
    expect_call(addr, "increase_balance_with_multiple_values", [1, 2, 3])
    call(addr, "increase_balance_with_multiple_values", [1, 2, 3])
  %}

  return ();
}

func test_expect_call_with_stop() {
  %{
    addr = deploy_contract("./src/basic.cairo").ok.contract_address
    expect_call(addr, "get_balance", [])
    call(addr, "get_balance")
    stop_expect_call(addr, "get_balance", [])
  %}

  return ();
}

func test_expect_call_after_the_call() {
  %{
    addr = deploy_contract("./src/basic.cairo").ok.contract_address
    call(addr, "get_balance")
    expect_call(addr, "get_balance", [])
  %}

  return ();
}

func test_expect_call_wrong_address() {
  %{
    addr1 = deploy_contract("./src/basic.cairo").ok.contract_address
    addr2 = deploy_contract("./src/basic.cairo").ok.contract_address
    expect_call(addr1, "get_balance", [])
    call(addr2, "get_balance")
  %}

  return ();
}

func test_expect_call_wrong_calldata() {
  %{
    addr = deploy_contract("./src/basic.cairo").ok.contract_address
    expect_call(addr, "increase_balance_with_multiple_values", [1, 2, 3])
    call(addr, "increase_balance_with_multiple_values", [1, 2, 4])
  %}

  return ();
}

func test_expect_call_partial_fail() {
  %{
    addr = deploy_contract("./src/basic.cairo").ok.contract_address
    expect_call(addr, "increase_balance_with_multiple_values", [1, 2, 3, 4])
    call(addr, "increase_balance_with_multiple_values", [1, 2, 3])
  %}

  return ();
}

func test_expect_call_expected_but_not_found() {
  %{
    addr = deploy_contract("./src/basic.cairo").ok.contract_address
    expect_call(addr, "get_balance", [])
  %}

  return ();
}

func test_expect_call_wrong_function_called() {
  %{
    addr = deploy_contract("./src/basic.cairo").ok.contract_address
    expect_call(addr, "increase_balance", [10])
    call(addr, "increase_balance2", [10])
  %}

  return ();
}

func test_expect_call_after_stop() {
  %{
    addr = deploy_contract("./src/basic.cairo").ok.contract_address
    expect_call(addr, "get_balance", [])
    stop_expect_call(addr, "get_balance", [])
    call(addr, "get_balance")
  %}

  return ();
}
