from starkware.starknet.common.syscalls import (
    get_block_timestamp,
    get_caller_address,
    get_block_number,
)
from starkware.cairo.common.math import assert_not_equal
from starkware.starknet.common.syscalls import storage_read, storage_write
from starkware.cairo.common.uint256 import Uint256

func test_fails_when_not_pranked() {
    %{
        contract_address = deploy_contract("tests/integration/pure_cairo_vm/cheatcodes/prank/pranked.cairo").unwrap().contract_address

        call(contract_address, "assert_pranked").unwrap()
    %}
    return ();
}

func test_not_fails_when_pranked() {
    %{
        EXPECTED_PRANKED_ADDRESS = 123
        contract_address = deploy_contract("tests/integration/pure_cairo_vm/cheatcodes/prank/pranked.cairo").unwrap().contract_address

        prank(EXPECTED_PRANKED_ADDRESS, contract_address).unwrap()
        call(contract_address, "assert_pranked").unwrap()
    %}
    return ();
}

func test_fails_when_different_target_is_pranked() {
    %{
        PRANKED_ADDRESS = 123
        contract_address = deploy_contract("tests/integration/pure_cairo_vm/cheatcodes/prank/pranked.cairo").unwrap().contract_address
        another_contract_address = deploy_contract("tests/integration/pure_cairo_vm/cheatcodes/prank/pranked.cairo").unwrap().contract_address 

        prank(PRANKED_ADDRESS, target_address=another_contract_address).unwrap()
        call(contract_address, "assert_pranked").unwrap()
    %}
    return ();
}

func test_not_fails_when_pranked_wrong_target() {
    %{ prank(123, target_address=123).unwrap() %}
    return ();
}
