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
        contract_address = deploy_contract("pranked").ok.contract_address

        assert call(contract_address, "assert_pranked").err_code == 0
    %}
    return ();
}

func test_not_fails_when_pranked() {
    %{
        EXPECTED_PRANKED_ADDRESS = 123
        contract_address = deploy_contract("pranked").ok.contract_address

        assert prank(EXPECTED_PRANKED_ADDRESS, contract_address).err_code == 0
        assert call(contract_address, "assert_pranked").err_code == 0
    %}
    return ();
}

func test_fails_when_different_target_is_pranked() {
    %{
        PRANKED_ADDRESS = 123
        contract_address = deploy_contract("pranked").ok.contract_address
        another_contract_address = deploy_contract("pranked").ok.contract_address

        assert prank(PRANKED_ADDRESS, target_address=another_contract_address).err_code == 0
        assert call(contract_address, "assert_pranked").err_code == 0
    %}
    return ();
}

func test_not_fails_when_pranked_wrong_target() {
    %{ assert prank(123, target_address=123).err_code == 0 %}
    return ();
}
