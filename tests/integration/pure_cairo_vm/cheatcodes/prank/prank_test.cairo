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
        contract_address = deploy_contract("./tests/integration/cheatcodes/prank/pranked.cairo").contract_address

        call(contract_address, "assert_pranked")
    %}
    return ();
}

func test_not_fails_when_pranked() {
    %{
        EXPECTED_PRANKED_ADDRESS = 123
        contract_address = deploy_contract("./tests/integration/cheatcodes/prank/pranked.cairo").contract_address

        prank(EXPECTED_PRANKED_ADDRESS, contract_address)
        call(contract_address, "assert_pranked")
    %}
    return ();
}

func test_fails_when_different_target_is_pranked() {
    %{
        PRANKED_ADDRESS = 123
        contract_address = deploy_contract("./tests/integration/cheatcodes/prank/pranked.cairo").contract_address
        another_contract_address = deploy_contract("./tests/integration/cheatcodes/prank/pranked.cairo").contract_address 

        prank(PRANKED_ADDRESS, target_contract_address=another_contract_address)
        call(contract_address, "assert_pranked")
    %}
    return ();
}

func test_prank_wrong_target() {
    %{ prank(123, target_contract_address=123) %}
    return ();
}

func test_fails_but_cannot_freeze_when_cheatcode_exception_is_raised() {
    %{
        prank(123, target_contract_address=123)
        prank(123, target_contract_address=123)
    %}
    return ();
}
